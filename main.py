# coding: UTF-8
#
# FILE        :main.py
# DATE        :2017.12.04
# DESCRIPTION :メインプログラム
# NAME        :Hikaru Yoshida
#

from google.appengine.ext import ndb        # Datastore API
from google.appengine.api import memcache   # Memcache API
from datetime import timedelta              # 相対時間型

import datetime                             # 日時型
import jinja2                               # ページの描画
import os                                   # OSインターフェイス
import webapp2                              # App Engineのフレームワーク

from datetime import Name                   # Nameデータ
from datetime import Data                   # Dataデータ

# テンプレートファイルを読み込む環境を作成
JINJA_ENVIRONMENT = jinja2.Environment( \
    loader     = jinja2.FileSystemLoader(os.path.dirname(__file__)), \
    extensions = ['jinja2.ext.autoescape'],autoescape=True)

# Valueクラス宣言
class Value:
    def __init__(self, t, d):
        self.time = t
        self.data = d

# URLから対応する関数の呼び出し
class BaseHandler(webapp2.RequestHandler):
    def render(self,html,values={}):
        template = JINJA_ENVIRONMENT.get_template(html)
        self.response.write(template.render(values))

# /      トップページ
class HomePage(BaseHandler):
    # ページ読み込み時処理
    def get(self):
        self.render('home.html')

# /graph グラフ表示
class GraphPage(BaseHandler):
    # ページ読み込み時処理
    def get(self):
        # Name取得
        names = Name.get()

        # Data取得
        datas = []
        for name in names:
            datas.append(Data.get(name.id, datetime.datetime(2017, 11, 22)))

        # value作成
        values = []
        time = datetime.datetime.combine(datetime.datetime(2017, 11, 22), datetime.time.min)
        while time < datetime.datetime.combine(datetime.datetime(2017, 11, 22), datetime.time.max):
            # センサ値集計リスト生成
            new_data = []
            for data in datas:
                try:
                    new_data.append(next((dv for dv in data if dv.date > time and dv.date < (time + timedelta(minutes=1))),None).val)
                except:
                    new_data.append('null')

            values.append(Value(time.strftime('%Y,%m,%d,%H,%M,0'), new_data))
            time = time + timedelta(minutes=1)

        outputs = {
            'header': names,
            'value': values,
            'number': len(names)
        }
        self.render('graph.html', outputs)

# URL - 関数 対応
app = webapp2.WSGIApplication([
    ('/',HomePage),
    ('/graph', GraphPage),
])
