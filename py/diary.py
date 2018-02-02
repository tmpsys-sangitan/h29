# coding: UTF-8
'''
FILE        :diary.py
DATE        :2018.01.17
DESCRIPTION :日誌管理モジュール
NAME        :Hikaru Yoshida
'''

from datetime import datetime as dt         # datatime型
from google.appengine.api import memcache   # Memcache API
from google.appengine.api import taskqueue  # TaskQueue API
import cloudstorage as storage              # GCS API
import logging                              # ログ出力

from py import gcs                          # GCS操作
from py import sensor                       # センサ管理
from py import utility                      # 汎用関数



def keycache(date, devid):
    """
    Memcacheキーの生成
    """
    if date is None:
        return "data_latest_" + devid
    elif isinstance(date, dt):
        return "data_" + utility.d2str(date) + "_" + devid
    return "data_" + date + "_" + devid



def keystr(date):
    """
    Storageキーの生成
    """
    if isinstance(date, dt):
        return "data_" + utility.d2str(date) + ".json"
    return "data_" + date + ".json"



def read(date, devid):
    """
    日誌をMemcacheから読み込む
    """

    # Memcacheから日誌データの読み込み
    djson = memcache.get(keycache(date, devid))
    if djson is None:
        # 日誌をStorageから読み込みキャッシュに保存
        cache(date)
        # Memcacheから日誌データを再度読み込み
        djson = memcache.get(keycache(date, devid))

    return djson



def cache(date):
    """
    日誌をStorageから読み込み、Memcacheへ保存する
    """

    # StorageからJSONを読み込み
    str_json = gcs.read_file(keystr(date))

    # jsonを辞書に変換
    dic = utility.load_json(str_json)

    # jsonを分解し、Memcacheへ保存
    for devid in sensor.get_list_devid("temp"):
        if devid in dic:
            memcache.add(keycache(date, devid), utility.dump_json(dic[devid]))
        else:
            memcache.add(keycache(date, devid), utility.dump_json({devid : {}}))
        logging.debug("DIARY CACHE : WRITE %s", keycache(date, devid))

    return



def new(date, devid):
    """
    日誌を新規作成
    """

    # 新規作成するjsonの雛形を作る
    dic = {
        devid : {}
    }

    # 辞書をjsonに変換
    njson = utility.dump_json(dic)

    # Storageにアップロード
    gcs.write_file(keystr(date), njson, "application/json")

    return njson



def add(date, devid, intensity, voltage, val, digital):
    """ 日誌に新たなデータを仮追加する
        @date  日付
        @devid 機器ID
    """

    # キャッシュから日誌データの読み込み
    try:
        diary_json = read(date, devid)
        diary_dic = utility.load_json(diary_json)
    except storage.NotFoundError:
        diary_dic = {}

    # データの重複チェック
    timekey = utility.t2str(date)
    if timekey in diary_dic:
        # 重複エラーで終了
        return

    # 新しいデータを辞書型に変換
    new_time = utility.t2str(date)
    new_data = {
        "intensity" : int(intensity),
        "voltage"   : int(voltage),
        "val"       : round(float(val), 1),
        "digital"   : int(digital)
    }

    # 辞書確認、なければ追加
    if devid not in diary_dic:
        diary_dic[devid] = {}

    # 新しいデータを辞書に追加してjsonに変換
    diary_dic[devid][new_time] = new_data
    diary_json = utility.dump_json(diary_dic)

    # キャッシュ更新
    memcache.delete(keycache(date, devid))
    memcache.add(keycache(date, devid), diary_json)

    # 最新温度データ更新
    memcache.delete(keycache(None, devid))
    memcache.add(keycache(None, devid), new_data)

    # リクエストを作成
    payload = utility.dump_json({
        'devid' : devid,
        'date'  : utility.d2str(date),
        'time'  : new_time,
        'data'  : new_data
    })

    # Storage更新リクエスト送信
    queue = taskqueue.Queue('StorageWriteRequestQueue')
    tasks = []
    tasks.append(taskqueue.Task(payload=payload, method='PULL'))
    queue.add(tasks)



def write():
    """ 日誌への仮追加を確定し、Storageに書き込む
    """

    # タスクの取得
    queue = taskqueue.Queue('StorageWriteRequestQueue')
    tasks = queue.lease_tasks(60, 100)

    # タスクが空でないなら
    if bool(tasks):
        # 作業用リストを生成
        temp_dic = {}

        # リクエストの消化
        for task in tasks:
            # リクエストから各データ取り出し
            payload = utility.load_json(task.payload)
            date = payload['date']
            devid = payload['devid']
            time = payload['time']
            data = payload['data']

            # 作業用辞書に読込済みか確認
            if date not in temp_dic:
                # 新しい辞書を作成
                temp_dic[date] = {}
                temp_dic[date]['task'] = []

                # StorageからJSONを読み込み作業用辞書に追加
                try:

                    gcs_json = gcs.read_file(keystr(date))
                    gcs_dic = utility.load_json(gcs_json)
                    temp_dic[date]['json'] = gcs_dic
                    logging.info("OPEN : %s", keystr(date))

                # Storageに新たなJSONを作成し作業用
                except storage.NotFoundError:
                    temp_dic[date]['json'] = {}
                    logging.info("DIARY WRITE : NEW %s", task.name)

            # taskの紐づけ
            temp_dic[date]['task'].append(task)

            # 辞書確認、なければ追加
            if devid not in temp_dic[date]['json']:
                temp_dic[date]['json'][devid] = {}

            # 辞書に新しいデータを追加
            temp_dic[date]['json'][devid][time] = data

        # 作業用辞書の変更をStorageにアップロード
        for (date, dic) in temp_dic.items():
            # 辞書型をJSONに変換
            gcs_json = utility.dump_json(dic['json'])

            # Storageにアップロード
            try:
                gcs.write_file(keystr(date), gcs_json, "application/json")
                logging.info("DIARY WRITE : %s", keystr(date))

            # エラーログ
            except storage.ServerError as error:
                logging.warning("DIARY WRITE : ERROR %s", error)

            # 成功した場合のみタスクを消去
            else:
                queue.delete_tasks(dic['task'])
