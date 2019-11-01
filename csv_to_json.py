# -*- coding: utf-8 -*-
# @Time    : 19-10-31 下午3:31
# @Author  : RenMeng

import pandas as pd
import json
import re

data = pd.read_csv('data.csv')
data = data.fillna('')
nrows = data.shape[0]

for j in range(nrows):

    webdata = data.iloc[j].to_dict()
    tars = ['overview', 'property_taxes', 'new_homes',
            'price_history', 'similar_homes', 'new_listing', 'comparable_sales']

    for key in webdata:
        if key == 'local_commons':
            webdata[key] = re.sub('[^0-9A-Za-z!\?\.,:\"\"\'\' \n]', '', webdata[key])
        if key in tars and webdata[key] != '':
            try:
                webdata[key] = eval(webdata[key])
            except:
                v = webdata[key]
                v = re.findall('\((datetime.*?[^0-9])\)', v)
                new_v = []
                for _ele in v:
                    new_ele = re.sub('\)|datetime\.datetime\(', '', _ele).split(',')
                    new_v.append(['-'.join([i.strip() for i in new_ele[:3]]), new_ele[-2], eval(new_ele[-1])])
                webdata[key] = new_v
        elif key != '':
            ele = webdata[key].split('\n')
            if len(ele) > 1:
                webdata[key] = ele

        if key == 'comparable_sales':
            webdata[key] = [{ele[0]: ele[1] for ele in line} for line in webdata[key]]


    open('./result/trulia/trulia_output_{:d}.json'.format(j), 'w', encoding='utf-8').\
                    write(json.dumps(webdata, indent=4, ensure_ascii=False))