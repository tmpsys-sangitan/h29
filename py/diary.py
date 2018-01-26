# coding: UTF-8
#
# FILE        :diary.py
# DATE        :2018.01.17
# DESCRIPTION :日誌管理モジュール
# NAME        :Hikaru Yoshida
#

from datetime import datetime as dt         # datatime型
from google.appengine.api import memcache   # Memcache API
from google.appengine.api import taskqueue  # TaskQueue API
import errno
import json                                 # jsonファイル操作
import logging                              # ログ出力
import os

from py import gcs                               # GCS操作
from py import sensor                            # センサ管理
from py import utility                           # 汎用関数



def keycache(date, devid):
    """
    Memcacheキーの生成
    """
    if isinstance(date, dt):
        return "data_" + utility.d2str(date) + "_" + devid
    else:
        return "data_" + date + "_" + devid



def keystr(date):
    """
    Storageキーの生成
    """
    if isinstance(date, dt):
        return "data_" + utility.d2str(date) + ".json"
    else:
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
    for devid in get_list_devid("temp"):
        if devid in dic:
            memcache.add(keycache(date, devid), utility.dump_json(dic[devid]))
        else:
            memcache.add(keycache(date, devid), utility.dump_json({devid : {}}))
        logging.debug("DIARY CACHE : WRITE " + keycache(date, devid))

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



def add(date, devid, fi, bv, val, ad):
    """ 日誌に新たなデータを仮追加する
        @date  日付
        @devid 機器ID
    """

    try:
        # キャッシュから日誌データの読み込み
        djson = read(date, devid)
    except IOError:
        djson = new(date, devid)

    # jsonを辞書型に変換
    dic = utility.load_json(djson)

    # データの重複チェック
    timekey = utility.t2str(date)
    if timekey in dic[devid]:
        # 重複エラーで終了
        return

    # 新しいデータを辞書型に変換
    newdata = {
        "fi"    : int(fi),
        "bv"    : int(bv),
        "val"   : round(float(val), 1),
        "ad"    : int(ad)
    }

    # 新しいデータを辞書に追加してjsonに変換
    dic[devid][utility.t2str(date)] = newdata
    djson = utility.dump_json(dic)

    # キャッシュ更新
    memcache.delete(keycache(date, devid))
    memcache.add(keycache(date, devid), djson)

    # リクエストを作成
    payload = utility.dump_json({
        'devid' : devid,
        'date'  : utility.d2str(date),
        'time'  : utility.t2str(date),
        'data'  : newdata
    })

    # Storage更新リクエスト送信
    q = taskqueue.Queue('StorageWriteRequestQueue')
    tasks = []
    tasks.append(taskqueue.Task(payload=payload, method='PULL'))
    q.add(tasks)



def write():
    """ 日誌への仮追加を確定し、Storageに書き込む
    """

    # タスクの取得
    q = taskqueue.Queue('StorageWriteRequestQueue')
    tasks = q.lease_tasks(60, 100)

    # タスクが空でないなら
    if bool(tasks):
        # 作業用リストを生成
        slist_date = []
        slist_dic = []

        # リクエストの消化
        for task in tasks:
            # リクエストから各データ取り出し
            payload = utility.load_json(task.payload)

            date  = payload['date']
            devid = payload['devid']
            time  = payload['time']
            data  = payload['data']

            # 作業用リストからJSONを読み込み
            if date not in slist_date:
                # StorageからJSONを読み込み作業用辞書に追加
                try:
                    str_json = gcs.read_file(keystr(date))
                    str_dic = utility.load_json(str_json)
                    slist_dic.append(str_dic)
                    slist_date.append(date)
                except:
                    slist_dic.append(new(date, devid))
                    logging.info("DIARY WRITE : NEW " + task.name)
                else:
                    logging.info("OPEN : " + keystr(date))

            # index取得
            index = slist_date.index(date)

            # 辞書確認、なければ追加
            if devid not in slist_dic[index]:
                slist_dic[index][devid] = {}

            # 辞書に新しいデータを追加
            slist_dic[index][devid][time] = data

        # 作業用辞書の変更をStorageにアップロード
        try:
            for (date, dic) in zip(slist_date, slist_dic):
                # 辞書型をJSONに変換
                str_json = utility.dump_json(dic)

                # Storageにアップロード、成功したらタスクを消去
                try:
                    gcs.write_file(keystr(date), str_json, "application/json")
                    logging.info("DIARY WRITE : " + keystr(date))
                except:
                    pass
        except:
            logging.info(str_json)
        else:
            q.delete_tasks(tasks)
