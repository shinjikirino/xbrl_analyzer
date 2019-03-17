import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
import json
import os
import sys
import csv
import pandas as pd
import datetime
from urllib import parse

from AbstractUfoCatcherWrapper import AbstractUfoCatcherWrapper

BASE_URL = 'http://resource.ufocatch.com/atom/tdnet/query/'
NAMESPACE = '{http://www.w3.org/2005/Atom}'


class TDnetCatcher(AbstractUfoCatcherWrapper):
    def __init__(self):
        self.url = BASE_URL
        self.namespace = NAMESPACE

    def _get_target_info_dict(self, tree, target_name, namespace, date_from, date_to):
        target_dict = defaultdict(dict)
        for el in tree.findall('.//' + namespace + 'entry'):
            title = el.find(namespace + 'title').text  # 要素のタイトル
            date_full = el.find(namespace + 'updated').text  # その要素が登録された日付(TZや時刻込)
            date = self._convert_str_to_date(date_full[0:10])  # 年月日だけ抽出
    
            if not (date_from <= date and date <= date_to): continue  # 日付でフィルタ
            if not target_name in str(title) : continue  # タイトルでフィルタ
    
            _id = el.find(namespace + 'id').text
            xml_url = ''
            for link in el.findall('./' + namespace + 'link[@type="text/xml"]'):
                url = link.attrib['href']
                if not ("Summary" in url and ".xml" in url): continue # Summaryのxmlだけ抽出
                xml_url = url
                break

            target_dict[_id] = {'id':_id, 'title':title, 'url':xml_url, 'date':date_full}
        return target_dict
    
    
    def _download_file(self, t_symbol, info, output_dir):    
        if info['url'] == "": return
        response = requests.get(info['url'])
        if response.ok:
            save_path = output_dir + '/' + t_symbol + '/'
            os.makedirs(save_path, exist_ok=True)
            with open(save_path + info['id'] + '.xml', mode='w') as f:
                f.write(response.content.decode())
