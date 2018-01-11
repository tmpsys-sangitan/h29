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
import datetime                             # 日時型
import jinja2                               # ページの描画
import os                                   # OSインターフェイス
import webapp2                              # App Engineのフレームワーク

import data                                 # データ管理モジュール

# テンプレートファイルを読み込む環境を作成
env = jinja2.Environment( \
    loader     = jinja2.FileSystemLoader(os.path.dirname(__file__)), \
    extensions = ['jinja2.ext.autoescape'],autoescape=True)

# ページの表示
class BaseHandler(webapp2.RequestHandler):
    def render(self,tpl,values={}):
        tpl_file = env.get_template(tpl)
        self.response.write(tpl_file.render(values))

# /       メインページ
class MainPage(BaseHandler):
    # ページ読み込み時処理
    def get(self):
        self.render('top.tpl')

# /upload アップロードページ
class UploadPage(BaseHandler):
    # ページ読み込み時処理
    # ページ読み込み時処理
    def get(self):
        self.render('upload.tpl')

    # 送信
    def post(self):
        # JSON読み込み
        daylog = data.Daylog(self.request.get('id'), self.request.get('date'))

        # JSON書き込み
        daylog.write(self.request.get('date'), self.request.get('fi'), \
                     self.request.get('bv'), self.request.get('val'), self.request.get('ad'))

        # 更新
        self.redirect('/upload')

# URL - 関数 対応
app = webapp2.WSGIApplication([
    ('/',       MainPage),
    ('/upload', UploadPage)
])

