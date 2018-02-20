# coding: UTF-8

"""
FILE        :main.py
DATE        :2017.12.04
DESCRIPTION :メインプログラム
NAME        :Hikaru Yoshida
"""

from datetime import datetime as dt         # datatime型
from datetime import timedelta      # 相対時間型
import cgi                                  # URLクエリ文の取得
import cloudstorage as storage              # GCS API
import jinja2                               # ページの描画
import os                                   # OSインターフェイス
import webapp2                              # App Engineのフレームワーク

from api.v1 import api                      # バックエンドプログラム

# テンプレートファイルを読み込む環境を作成
ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'], autoescape=True)



class BaseHandler(webapp2.RequestHandler):
    """ページの表示
    """

    def render(self, tpl, values=None):
        """ページの表示

        Arguments:
            tpl {[string]} -- ベースになるhtml/tplファイル名
            values {[dictionary]} -- 入力するパラメータ
        """
        # valuesに指定がないなら空辞書を生成
        values = values or {}

        # テンプレートを組み立ててレスポンスに書く
        self.response.headers['cache-control'] = 'public, max-age=3600'
        self.response.headers['content-type'] = 'text/html; charset=utf-8'
        tpl_file = ENV.get_template(tpl)
        self.response.write(tpl_file.render(values))



class MainPage(BaseHandler):
    """/       メインページ
    """

    def get(self):
        """ページ読み込み時処理
        """

        # リストの値を取得
        values = {
            'periods': api.getPeriods(),
            'tags'   : api.getTags(),
            'kinds'  : api.getKinds(),
        }

        self.render('template/main.html', values)



class PostUpload(BaseHandler):
    """/upload アップロードページ
    """

    def get(self):
        """ページ読み込み時処理
        """
        self.render('template/upload.html')

    def post(self):
        """送信時処理
        """

        # パラメータ読み込み
        datestr = cgi.escape(self.request.get("date"))
        devid = cgi.escape(self.request.get("devid"))

        # データ辞書作成
        data = {}
        try:
            data['i'] = int(self.request.get("i"))
        except ValueError:
            pass
        try:
            data['v'] = int(self.request.get("v"))
        except ValueError:
            pass
        try:
            data['p1'] = round(float(self.request.get("p1")), 1)
        except ValueError:
            pass
        try:
            data['p2'] = round(float(self.request.get("p2")), 1)
        except ValueError:
            pass
        try:
            data['p3'] = round(float(self.request.get("p3")), 1)
        except ValueError:
            pass
        try:
            data['p4'] = round(float(self.request.get("p4")), 1)
        except ValueError:
            pass
        try:
            data['a1'] = int(self.request.get("a1"))
        except ValueError:
            pass
        try:
            data['a2'] = int(self.request.get("a2"))
        except ValueError:
            pass
        try:
            data['a3'] = int(self.request.get("a3"))
        except ValueError:
            pass
        try:
            data['a4'] = int(self.request.get("a4"))
        except ValueError:
            pass

        api.addDiary(datestr, devid, data)

class PostWrite(BaseHandler):
    """仮追加を確定し、Storageに書込む
    """

    @classmethod
    def get(cls):
        """ページ読み込み時処理
        """
        api.updateDiary()



class GetDiary(BaseHandler):
    """日誌データの送信
    """

    def get(self):
        """ページ読み込み時処理
        """
        # パラメータ読み込み
        date = cgi.escape(self.request.get("date"))
        tag = cgi.escape(self.request.get("tag"))
        kind = cgi.escape(self.request.get("kind"))

        api.getGraph(self, date, tag, kind)



class GetLatest(BaseHandler):
    """最新温度データの送信
    """

    def get(self):
        """ページ読み込み時処理
        """
        # パラメータ読み込み
        kind = cgi.escape(self.request.get("kind"))
        api.getLatest(self, kind)


# URL - 関数 対応
app = webapp2.WSGIApplication([
    # ページ
    webapp2.Route('/', MainPage),

    # POST
    webapp2.Route('/upload', PostUpload),
    webapp2.Route('/write', PostWrite),

    # GET
    webapp2.Route('/diary', GetDiary),
    webapp2.Route('/latest', GetLatest),
])
