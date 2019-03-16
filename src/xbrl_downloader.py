import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
import json
import os
from zipfile import ZipFile
from io import BytesIO
import sys
import csv
import pandas as pd
import datetime

BASE_URL = 'http://resource.ufocatch.com/atom/edinetx/query/'
NAMESPACE = '{http://www.w3.org/2005/Atom}'
TARGET_NAME = u'有価証券報告書'

def get_target_info_dict(tree, target_name, namespace, date_from, date_to):
    target_dict = defaultdict(dict)
    for el in tree.findall('.//' + namespace + 'entry'):
        title = el.find(namespace + 'title').text  # 要素のタイトル
        date_full = el.find(namespace + 'updated').text  # その要素が登録された日付(TZや時刻込)
        date = convert_str_to_date(date_full[0:10])  # 年月日だけ抽出

        if not (date_from <= date and date <= date_to): continue  # 日付でフィルタ
        if not target_name in str(title) : continue  # タイトルでフィルタ

        _id = el.find(namespace + 'id').text
        link = el.find('./' + namespace + 'link[@type="application/zip"]')
        url = link.attrib['href']
        target_dict[_id] = {'id':_id, 'title':title, 'url':url, 'date':date_full}
    return target_dict


def download_xbrl_file(t_symbol, info, output_dir):    
    response = requests.get(info['url'])
    if response.ok:
        save_path = output_dir + '/' + t_symbol + '/' + _id
        os.makedirs(save_path, exist_ok=True)
        z = ZipFile(BytesIO(response.content))
        z.extractall(save_path)


def dump_info(t_symbol, dump_info, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with open(output_dir + '/' + t_symbol + '.json', 'w') as of:
        json.dump(dump_info, of, indent=4)


def convert_str_to_date(date_str):
    year, month, day = date_str.split("-")
    return datetime.date(int(year), int(month), int(day))


if __name__=='__main__':

    args = sys.argv

    codelist_file = str(args[1])
    start_date = str(args[2])
    end_date = str(args[3])
    xbrl_output_dir = str(args[4])
    if len(args) == 7:
        dump_mode = str(args[5])
        dump_output_dir = str(args[6])
    else:
        dump_mode = ""
        dump_output_dir = ""

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

    print("out dir:" + '\t' + str(xbrl_output_dir))
    # コマンドライン引数から、パース結果をdumpするか選ぶ
    has_dump_request = True if dump_mode != "" else False
    if has_dump_request:
        print("dump mode:" + '\t' + str(has_dump_request))
        print("dump dir:" + '\t' + str(dump_output_dir))

    target_xbrl_dict = defaultdict(dict)  # 対象のxbrl群
    for t_symbol in t_symbols:
        symbol_info_xml = requests.get(BASE_URL + t_symbol).text  # 各銘柄のxbrlがあるurlを取得
        symbol_info_tree = ET.fromstring(symbol_info_xml.encode('utf-8'))
        ET.register_namespace('',NAMESPACE[1:-1])  # namespace付きなのでnamespaceをelementtreeに登録
        target_xbrl_dict[t_symbol] = get_target_info_dict(symbol_info_tree, TARGET_NAME, NAMESPACE, date_from, date_to)

    for t_symbol, info_dict in target_xbrl_dict.items():  # urlからxbrlをダウンロード
        print(str(t_symbol) + ':')
        for _id, info in info_dict.items():
            print('\t' + (info['title']))
            download_xbrl_file(t_symbol, info, xbrl_output_dir)
        if has_dump_request:
            print("dump info...")
            dump_info(t_symbol, info_dict, dump_output_dir)
