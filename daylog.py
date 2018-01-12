# coding: UTF-8
#
# FILE        :daylog.py
# DATE        :2018.01.10
# DESCRIPTION :日誌管理モジュール
# NAME        :Hikaru Yoshida
#

from google.appengine.api import memcache   # Memcache API
from datetime import datetime as dt         # datatime型
import json                                 # jsonファイル操作

import gcs                                  # GCS操作

class daylog:
    """ 日誌クラス
        @id   センサID
        @date 日付
        @json jsonデータ
    """

    def __init__(self, id, date):
        """ 指定された日付のデータを読み込む
            @id   参照するセンサのID
            @date 参照する日付
        """
        self.id = id
        self.date = dt.strptime(date[0:8], '%Y%m%d')
        if self.read() != 1:
            self.new()

    def gen_key(self):
        """ キーの生成
        """
        return "date_" + self.id + "_" + self.date.strftime('%Y%m%d')

    def write(self, date, fi, bv, val, ad):
        """ 日誌に書き込む
            @date 日付
            @fi   電波強度
            @bv   電池電圧
            @val  変換値
            @ad   AD値
        """

        # jsonを辞書型に変換
        dic = json.loads(logjson)

        # dateを文字列型→日時型→文字列型に再変換
        date = dt.strptime(date, '%Y%m%d%H%M%S')
        date = date.strftime('%Y/%m/%d %H:%M:%S') + " +0900"

        # 新しいデータを辞書型に変換
        newdata = {
            "date"  : date,
            "fi"    : int(fi),
            "bv"    : int(bv),
            "val"   : float(val),
            "ad"    : int(ad)
        }

        # 新しいデータを辞書に追加
        dic["datas"].append(newdata)

        # 辞書をjsonに
        logjson = json.dumps(dic)

        # キャッシュ更新
        memcache.delete(self.gen_key())
        memcache.add(self.gen_key(), logjson)

        # GCS更新
        gcs.write_file(self.gen_key() + ".json", logjson, "application/json")

    def read(self):
        """ 日誌を読み込む
        """

        # キャッシュ問い合わせ
        logjson = memcache.get(self.gen_key())
        if logjson is None:
            # ないならGCSから読み込み
            try:
                logjson = gcs.read_file(self.gen_key() + ".json")
            except:
                return None
            else:
                memcache.add(self.gen_key(), logjson)

        return logjson

    def new(self):
        """ 日誌を新規作成
        """
        dic = {
            "name"  : "教官室",
            "id"    : self.id,
            "type"  : "temp",
            "datas" : []
        }

        # 辞書をjsonに
        logjson = json.dumps(dic)

        # GCS作成
        gcs.write_file(self.gen_key() + ".json", logjson, "application/json")