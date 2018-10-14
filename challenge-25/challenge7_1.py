# -*- coding: utf-8 -*-
import pandas as pd


def co2():

    # 读取数据集
    df_climate = pd.read_excel("ClimateChage.xlsx", sheetname='表名')