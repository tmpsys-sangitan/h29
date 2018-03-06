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

import model                        # GCS操作
import sensor                       # センサ管理
import utility                      # 汎用関数

class Diary(object):
    """ 日誌管理

    Members:
        cache {DiaryCache} 同じ日付のキャッシュ
        date  {datatime}   日誌の日付
        name  {string}     対応するファイル名
    """

    def __init__(self, date):
        """ 日誌の初期化

        Arguments:
            date  {datatime} -- 日付
        """
        self.cache = {}
        self.date = date
        self.storage = DiaryStorage(date)

        # キャッシュ名の設定
        for devid in sensor.get_list_devid():
            self.cache[devid] = DiaryCache(date, devid)

    def add(self, date, devid, data):
        """ 日誌に新たなデータを仮追加する

        Arguments:
            date  {datetime}   -- 日付
            devid {string}     -- 機器ID
            data  {dictionary} -- 保存するパラメータの辞書
        """
        self.cache[devid].add(date, data)
        Latest.updateLatest(devid, data)
        RequestQueue().add(date, devid, data)

    def get(self, date, devid):
        """ 日誌の読み込み

        Arguments:
            date  {datetime} -- 日付
            devid {string}   -- 機器ID
        """
        res = self.cache[devid].get()
        if not bool(res):
            try:
                self.edit(self.read())
                res = self.cache[devid].get()
            except storage.errors.NotFoundError:
                logging.debug(self.storage.name + "MISS")
        return res or {} # res、resがNoneなら空辞書を返す

    def read(self):
        """ 日誌をGCSから読み込む
        """
        return self.storage.read()

    def edit(self, dic):
        """ jsonを分解し、Memcacheへ保存

        Arguments:
            dic {dictionary} -- GCSから読み込んだ日誌データ
        """
        for devid in sensor.get_list_devid():
            if devid in dic:
                self.cache[devid].subst(dic[devid])
            else:
                self.cache[devid].subst({devid : {}})
            logging.debug("DIARY CACHE : WRITE %s", self.cache[devid].name)

    @staticmethod
    def updateDiary():
        """ 日誌への仮追加を確定し、Storageに書き込む
        """
        # タスクが空でないなら
        queue = RequestQueue()
        if queue.read():
            # 作業用辞書を生成
            wip_tasks = {}
            wip_diary = {}

            # リクエストの消化
            for task in queue.tasks:
                date, devid, time, data = RequestQueue.parse(task)

                # 作業用辞書に読込済みか確認
                if date not in wip_diary:
                    wip_tasks[date] = []
                    wip_diary[date] = DiaryStorage(date)
                    wip_diary[date].read()

                # taskの紐づけ
                wip_tasks[date].append(task)

                # 辞書に新しいデータを追加
                wip_diary[date].add(devid, time, data)

            # 作業用辞書をStorageにアップロード
            for (date, dic) in wip_diary.items():
                try:
                    dic.write()
                except Exception, error:
                    raise error
                else:
                    queue.delete(wip_tasks[date])


class DiaryCache(model.Cache, object):
    """ 日誌キャッシュ管理
    """

    def __init__(self, date, devid):
        """ キャッシュキーの登録

        Arguments:
            date  {datatime} -- 日付
            devid {string}   -- 機器ID
        """
        super(DiaryCache, self).__init__("data" + "_" + utility.d2str(date) + "_" + devid)

    def add(self, date, data):
        """ 日誌に新たなデータを仮追加する

        Arguments:
            date  {datatime}   -- タイムスタンプ
            data  {dictionary} -- 保存するパラメータの辞書
        """
        target = self.get()

        # 新しいデータを辞書に追加してjsonに変換
        timekey = utility.t2str(date)
        if timekey in target:
            # 重複しているならエラーを返す
            raise RuntimeError("キーが重複しています")
        target[timekey] = data

        super(DiaryCache, self).add(target)

    def subst(self, data):
        """[summary]

        Arguments:
            data {dictionary} -- キャッシュへの保存
        """
        super(DiaryCache, self).add(data)


class DiaryStorage(object):

    def __init__(self, date):
        """ ストレージの初期化

        Arguments:
            date {datetime or string} -- 日付
        """
        self.name = "data_" + utility.d2str(date) + ".json"
        self.dic = {}

    def add(self, devid, time, data):
        """[summary]

        Arguments:
            devid {string}     -- 機器ID
            time  {string}     -- 時刻
            data  {dictionary} -- データ
        """
        if devid not in self.dic:
            self.dic[devid] = {}
        self.dic[devid][time] = data

    def read(self):
        """ GCSから読み込み

        Returns:
            dictionary -- 読み込んだ辞書
        """
        try:
            self.dic = utility.load_json(model.Storage.read_file(self.name))
            logging.info("OPEN : %s", self.name)
        except storage.NotFoundError:
            self.dic = {}
            logging.info("DIARY WRITE : NEW %s", self.name)
        return self.dic

    def write(self):
        """ GCSへ書き込み
        """
        try:
            model.Storage.write_file(self.name, utility.dump_json(self.dic), "application/json")
            logging.info("DIARY WRITE : %s", self.name)

        except storage.ServerError as error:
            logging.warning("DIARY WRITE : ERROR %s", error)
            raise error

class RequestQueue(object):
    """ タスクキュー
    """
    def __init__(self):
        """ キューの取得
        """
        self.queue = taskqueue.Queue('StorageWriteRequestQueue')
        self.tasks = []

    def add(self, date, devid, data):
        """[summary]

        Arguments:
            date  {datetime}   -- タイムスタンプ
            devid {string}     -- 機器ID
            data  {dictionary} -- 新しいデータ
        """
        tasks = []
        tasks.append(taskqueue.Task(payload=utility.dump_json({
            'devid' : devid,
            'date'  : utility.d2str(date),
            'time'  : utility.t2str(date),
            'data'  : data,
        }), method='PULL'))
        self.queue.add(tasks)

    def read(self):
        """ キューからタスクをリースする

        Returns:
            bool -- キューが空ならfalse
        """
        self.tasks = self.queue.lease_tasks(60, 100)
        return bool(self.tasks)

    def delete(self, tasks):
        """ キューからタスクを削除する

        Arguments:
            tasks {task list} -- 削除するタスク
        """
        self.queue.delete_tasks(tasks)

    @staticmethod
    def parse(task):
        """ 対応するタスクをパースする

        Returns:
            string     -- 日付
            string     -- 機器ID
            string     -- 時刻
            dictionary -- データ
        """
        pl = utility.load_json(task.payload)
        return pl['date'], pl['devid'], pl['time'], pl['data']


class Latest(model.Cache):
    """ 最新データ
    """

    def __init__(self, kind):
        """ キャッシュの実体化

        Arguments:
            kind {string} -- データ種類
        """
        super(Latest, self).__init__("data_latest_" + kind, charset='unicode')
        self.kind = kind

    def add(self, devid, val):
        """ 最新データの更新

        Arguments:
            devid {string} -- 機器ID
            val   {any}    -- 値
        """
        latests = self.get()
        latests[sensor.get_mapid(devid)] = val
        super(Latest, self).add(latests)

    @staticmethod
    def updateLatest(devid, datas):
        """ データを分解してそれぞれの最新データに更新する

        Arguments:
            devid {string}     -- 機器ID
            datas {dictionary} -- データの辞書
        """
        for data in datas.items():
            Latest(data[0]).add(devid, data[1])
