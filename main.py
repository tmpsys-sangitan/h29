# coding: UTF-8
#
# FILE        :main.py
# DATE        :2017.12.04
# DESCRIPTION :メインプログラム
# NAME        :Hikaru Yoshida
#

from google.appengine.ext import ndb        # Datastore API
from google.appengine.api import memcache   # Memcache API
import cgi                                  # URLクエリ文の取得
import jinja2                               # ページの描画
import logging                              # ログ出力
import os                                   # OSインターフェイス
import urllib2                              # URLを開く
import webapp2                              # App Engineのフレームワーク

from py import diary                        # 日誌管理モジュール
from py import sensor                       # センサ管理
from py import utility                      # 汎用関数

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
        self.render('tpl/main.tpl')


# /upload アップロードページ
class PostUpload(BaseHandler):
    # ページ読み込み時処理
    def get(self):
        self.render('tpl/upload.tpl')

    # 送信
    def post(self):
        # パラメータ読み込み
        devid = cgi.escape(self.request.get("devid"))
        date  = cgi.escape(self.request.get("date"))
        fi    = cgi.escape(self.request.get("fi"))
        bv    = cgi.escape(self.request.get("bv"))
        val   = cgi.escape(self.request.get("val"))
        ad    = cgi.escape(self.request.get("ad"))

        # 日誌に仮追加
        diary.add(utility.str2dt(date), devid, fi, bv, val, ad)


# 仮追加を確定し、Storageに書込む
class PostWrite(BaseHandler):
    def get(self):
        diary.write()


# 日誌データの送信
class GetDiary(BaseHandler):
    # ページ読み込み時処理
    def get(self):
        # パラメータ読み込み
        date  = cgi.escape(self.request.get("date"))
        mapid = cgi.escape(self.request.get("mapid"))
        type  = cgi.escape(self.request.get("type"))

        # マップIDを機器IDに変換
        devid = sensor.get_devid(mapid, type)

        # Nullチェック
        if devid is None:
            logging.info("MAIN GETDIARY : DEVID IS NONE")
            return

        # JSONを返却
        self.response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
        self.response.out.write(
            "%s(%s)" %
            (urllib2.unquote(self.request.get('callback')),
            diary.read(date, devid))
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
