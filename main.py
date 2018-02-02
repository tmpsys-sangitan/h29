# coding: UTF-8

"""
FILE        :main.py
DATE        :2017.12.04
DESCRIPTION :メインプログラム
NAME        :Hikaru Yoshida
"""

import cgi                                  # URLクエリ文の取得
import jinja2                               # ページの描画
import os                                   # OSインターフェイス
import webapp2                              # App Engineのフレームワーク
import cloudstorage as storage              # GCS API

from py import diary                        # 日誌管理モジュール
from py import graph                        # グラフデータモジュール
from py import heatmap                      # マップデータモジュール
from py import utility                      # 汎用関数

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
        # valseに指定がないなら空辞書を生成
        values = values or {}

        # テンプレートを組み立ててレスポンスに書く
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        tpl_file = ENV.get_template(tpl)
        self.response.write(tpl_file.render(values))



class MainPage(BaseHandler):
    """/       メインページ
    """

    def get(self):
        """ページ読み込み時処理
        """
        self.render('tpl/main.tpl')



class PostUpload(BaseHandler):
    """/upload アップロードページ
    """

    def get(self):
        """ページ読み込み時処理
        """
        self.render('tpl/upload.tpl')

    def post(self):
        """送信時処理
        """

        # パラメータ読み込み
        devid = cgi.escape(self.request.get("devid"))
        date = cgi.escape(self.request.get("date"))
        intensity = cgi.escape(self.request.get("fi"))
        voltage = cgi.escape(self.request.get("bv"))
        val = cgi.escape(self.request.get("val"))
        digital = cgi.escape(self.request.get("ad"))

        # 日誌に仮追加
        diary.add(utility.str2dt(date), devid, intensity, voltage, val, digital)



class PostWrite(BaseHandler):
    """仮追加を確定し、Storageに書込む
    """

    @classmethod
    def get(cls):
        """ページ読み込み時処理
        """
        diary.write()



class GetDiary(BaseHandler):
    """日誌データの送信
    """

    def get(self):
        """ページ読み込み時処理
        """
        # パラメータ読み込み
        date = cgi.escape(self.request.get("date"))
        # mapid = cgi.escape(self.request.get("mapid"))
        # type  = cgi.escape(self.request.get("type"))

        # JSONを返却
        try:
            resjson = graph.gen_dayly(date)
        except storage.NotFoundError:
            resjson = None

        if resjson is not None:
            self.response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
            self.response.out.write(
                "%s(%s)" %
                ('callback',
                graph.gen_dayly(date))
            )
        else:
            self.error(404)



class GetLatest(BaseHandler):
    """最新温度データの送信
    """

    def get(self):
        """ページ読み込み時処理
        """
        # パラメータ読み込み
        sensor_type = cgi.escape(self.request.get("type"))

        # JSONを返却
        self.response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
        self.response.out.write(
            "%s(%s)" %
            ('callback',
             heatmap.get_latest(sensor_type))
        )



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
