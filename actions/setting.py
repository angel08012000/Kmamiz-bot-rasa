import matplotlib.pyplot as plt
import pandas as pd
import requests
import json
import os


# PREFIX = "http://192.168.39.122:8084"
NAMESPACE = "book"
PREFIX = "https://kmamiz-demo.soselab.tw"
# IMAGES_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/images"
IMAGES_PATH = f"{os.getcwd()}/images"

INSIGHTS = ["cohesion", "coupling", "instability", "all insights"]
DEPENDENCIES = ["service dependency graph", "endpoint dependency graph", "direct service dependencies", "indirect service dependencies"]

def get_api(url):
    r = requests.get(url)

    if r.status_code!=requests.codes.ok:
        sys.exit(f"{r.status_code} 獲取 API 失敗！")

    # r.text 可以拿到回覆的內容，型態為 str
    response = json.loads(r.text) # str to json
    return response

def create_insight_table(data):
    df = pd.DataFrame(data)
    df.index = [''] * len(df)

    fig, ax = plt.subplots() # 建立圖表
    ax.axis('off') # 隱藏座標軸

    # 算每個 col 要多寬（全部加起來要是1）
    # temp = []
    # for key, val in data.items():
    #     temp.append(max( max(len(str(c)) for c in val) , len(str(key)) ))
    
    # total = sum(temp)
    # col_widths = [col/total for col in temp]

    # 建立表格，並將 data 放入
    # table = pd.plotting.table(ax, df, loc='center', cellLoc='center', colWidths=col_widths)
    table = pd.plotting.table(ax, df, loc='center', cellLoc='center', colWidths= [.4, .2, .2, .2])
    table.scale(1, 2) # 調整表格大小

    # 調整表格樣式
    for (i, j), cell in table._cells.items():
        cell.set_text_props(fontsize=12)

        if i == 0:
            cell.set_text_props(fontweight='bold', color='white')
            cell.get_text().set_fontsize(15)
            cell.set_facecolor('#1370ce')
            
        if i%2==0 and i:
            cell.set_facecolor('#d3d3d3')

    plt.savefig('images/table.png', bbox_inches='tight', pad_inches=0.1)

def create_all_insights_table(data):

    temp = {
        'cohesion': {'SIDC': 1, 'SIUC': 1, 'TSIC': 1},
        'coupling': {'AIS': 1, 'ADS': 0, 'ACS': 0},
        'instability': {'FanOut': 0, 'FanIn': 1, 'SDP': 0}
    }
    data = {
        "cohesion": ["SIDC", temp['cohesion']['SIDC'], "SIUC", temp['cohesion']['SIUC'], "TSIC", temp['cohesion']['TSIC']],
        "coupling": ["AIS", temp['coupling']['AIS'], "ADS", temp['coupling']['ADS'], "ACS", temp['coupling']['ACS']],
        "instability": ["FanOut", temp['instability']['FanOut'], "FanIn", temp['instability']['FanIn'], "SDP", temp['instability']['SDP']],
    }
    df = pd.DataFrame(data)
    df.index = [''] * len(df)

    fig, ax = plt.subplots() # 建立圖表
    ax.axis('off') # 隱藏座標軸

    # 建立表格，並將 data 放入
    # table = pd.plotting.table(ax, df, loc='center', cellLoc='center', colWidths=col_widths)
    table = pd.plotting.table(ax, df, loc='center', cellLoc='center')
    table.scale(1, 2) # 調整表格大小


    # 調整表格樣式
    for (i, j), cell in table._cells.items():
        cell.set_text_props(fontsize=12)

        if i==0:
            cell.set_text_props(fontweight='bold', color='white')
            cell.get_text().set_fontsize(15)
            cell.set_facecolor('#1370ce')
        if i and i%2:
            cell.set_text_props(fontweight='bold', color='white')
            cell.set_facecolor('#79A5D1')

    plt.savefig('images/table.png', bbox_inches='tight', pad_inches=0.1)

create_all_insights_table(1)