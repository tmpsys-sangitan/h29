# coding: UTF-8
#
# FILE        :main.py
# DATE        :2017.12.04
# DESCRIPTION :メインプログラム
# NAME        :Hikaru Yoshida
#

from google.appengine.ext import ndb        # Datastore API
from google.appengine.api import memcache   # Memcache API
from datetime import datetime as dt         # datatime型
from datetime import timedelta as td        # datatime型
import cgi                                  # URLクエリ文の取得
import datetime                             # 日時型
import jinja2                               # ページの描画
import os                                   # OSインターフェイス
import urllib2                              # URLを開く
import webapp2                              # App Engineのフレームワーク

from diary import diary                     # 日誌管理モジュール
import utility                              # 汎用関数

# テンプレートファイルを読み込む環境を作成
env = jinja2.Environment( \
    loader     = jinja2.FileSystemLoader(os.path.dirname(__file__)), \
    extensions = ['jinja2.ext.autoescape'],autoescape=True)

# ページの表示
class BaseHandler(webapp2.RequestHandler):
    def render(self, tpl, values={}):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        tpl_file = env.get_template(tpl)
        self.response.write(tpl_file.render(values))


# /       メインページ
class MainPage(BaseHandler):
    # ページ読み込み時処理
    def get(self):
        self.render('main.tpl')


# /upload アップロードページ
class PostUpload(BaseHandler):
    # ページ読み込み時処理
    def get(self):
        self.render('upload.tpl')

    # 送信
    def post(self):
        # パラメータ読み込み
        pdic = {
            # 機器ID
            "divid": cgi.escape(self.request.get("divid")),
            # 日時
            "date" : cgi.escape(self.request.get("date")),
            # 電波状況
            "fi" : cgi.escape(self.request.get("fi")),
            # 電源電圧
            "bv" : cgi.escape(self.request.get("bv")),
            # 値
            "val" : cgi.escape(self.request.get("val")),
            # A/D値
            "ad" : cgi.escape(self.request.get("ad"))
        }

        # 日誌に仮追加
        diary.add(dt.strptime(pdic['date'], '%Y%m%d%H%M%S'), pdic['divid'], pdic['fi'], pdic['bv'], pdic['val'], pdic['ad'])


# 仮追加を確定し、Storageに書込む
class PostWrite(BaseHandler):
    def get(self):
        # パラメータ読み込み
        date = utility.str2dt(cgi.escape(self.request.get("date")))

        # パラメータなしなら今日と昨日
        if date is None:
            # 日付の取得＆計算
            today = dt.now()
            ystd  = today - td(days = 1)

            # 呼び出し
            diary.write(today)
            diary.write(ystd)

        # パラメータありなら指定の日付
        else:
            diary.write(date)
            pass


class GetDiary(BaseHandler):
    # ページ読み込み時処理
    def get(self):
        # パラメータ読み込み
        date  = cgi.escape(self.request.get("date"))
        mapid = cgi.escape(self.request.get("mapid"))

        # JSON読み込み
        dl = diary(date, sensor.get_devid(mapid, temp), 'R')

        # JSONを返却
        self.response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
        self.response.out.write(
            "%s(%s)" %
            (urllib2.unquote(self.request.get('callback')),
            dl.read())
        )


# URL - 関数 対応
app = webapp2.WSGIApplication([
    # ページ
    webapp2.Route('/'      , MainPage),

    # POST
    webapp2.Route('/upload', PostUpload),
    webapp2.Route('/write' , PostWrite),

    # GET
    webapp2.Route('/diary' , GetDiary),
])
