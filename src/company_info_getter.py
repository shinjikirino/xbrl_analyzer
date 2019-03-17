import requests
from collections import defaultdict
import os
import sys
import csv
import pandas as pd
import datetime

import UfoCatcherWrapperFactory

def convert_str_to_date(date_str):
    year, month, day = date_str.split("-")
    return datetime.date(int(year), int(month), int(day))


if __name__=='__main__':

    args = sys.argv

    codelist_file = str(args[1])
    source = str(args[2])
    target_name = str(args[3])
    start_date = str(args[4])
    end_date = str(args[5])
    output_dir = str(args[6])
    #　コマンドライン引数から期間をパースする
    date_from = convert_str_to_date(start_date)
    date_to = convert_str_to_date(end_date)
    print("start_date:" + '\t' + date_from.strftime('%Y-%m-%d'))
    print("end_date:" + '\t' + date_to.strftime('%Y-%m-%d'))

    # コマンドライン引数のcsvから取得対象銘柄をパースする
    code_list = pd.read_csv(codelist_file, converters={"code":str}).fillna('')
    t_symbols = []  # 取得対象銘柄ろリスト
    for key, codes in code_list.iterrows():
      t_symbols.extend(codes)
    print("code_list:")
    print(t_symbols)

    print("out dir:" + '\t' + str(output_dir))

    factory = UfoCatcherWrapperFactory.UfoCatcherWrapperFactory()
    downloader = factory.create(source)
    downloader.download(t_symbols, target_name, date_from, date_to, output_dir)
