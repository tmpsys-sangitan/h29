# coding: UTF-8

'''
# FILE        :gcs.py
# DATE        :2017.12.18
# DESCRIPTION :Google Cloud Storage 操作モジュール
# URL         :http://tokibito.hatenablog.com/entry/20140514/1400076408
# '''

from google.appengine.api import app_identity
import cloudstorage as storage
import os



# GCSタイムアウト設定
RETRY_PARAMS = storage.RetryParams(
    initial_delay=0.2,
    max_delay=5.0,
    backoff_factor=2,
    max_retry_period=15)
storage.set_default_retry_params(RETRY_PARAMS)



def get_bucket_name():
    """ バケット名を返す
    """
    return os.environ.get(
        'BUCKET_NAME',
        app_identity.get_default_gcs_bucket_name())



def write_file(filename, content, content_type):
    """ GCSにファイル保存
        @filneame       ファイル名
        @content        内容
        @content_type   ファイルの種別
                        テキストなら'text/plain'
    """
    bucket_name = get_bucket_name()
    filepath = '/' + bucket_name + '/' + filename
    with storage.open(filepath, 'w', content_type=content_type) as gcs_file:
        gcs_file.write(content.encode('utf-8'))



def read_file(filename):
    """ GCSからファイルを読み込み
        @filneame       ファイル名
    """
    bucket_name = get_bucket_name()
    filepath = '/' + bucket_name + '/' + filename
    with storage.open(filepath) as gcs_file:
        return gcs_file.read()
