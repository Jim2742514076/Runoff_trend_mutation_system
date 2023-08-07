# -*-coding = utf-8 -*-
# @Time : 2023/8/2 15:39
# @Author : 万锦
# @File : arithmetic.py
# @Softwore : PyCharm

import numpy as np
from scipy.stats import linregress
import pandas as pd
from pymannkendall import original_test
import matplotlib.pyplot as plt
from PyEMD import EEMD

# 进行线性回归分析
def linear_regression(time_series,runoff_data):
    #time_series年份输入，runoff_data年均径流输入

    slope, intercept, r_value, p_value, std_err = linregress(time_series, runoff_data)
    return slope, intercept, r_value, p_value, std_err

#MK检验
def mk_test(runoff_data):
    # 进行MK检验
    result = original_test(runoff_data)
    return result

#累积距平趋势检验
def cumulative_anomaly(runoff_data):
    # 计算长期平均值
    runoff_data_mean = np.mean(runoff_data)
    # 计算距平序列
    departure_data = np.array(runoff_data) - runoff_data_mean
    # 计算累积距平序列
    cumulative_departure_data = np.cumsum(departure_data)
    return cumulative_departure_data

#emd趋势分析
def emd_trend(runoff_data):
    # 创建 EEMD 实例
    eemd = EEMD()
    # 进行 EMD 分解
    eemd_data = eemd.eemd(runoff_data)
    # 选择最低频的 IMF 作为趋势分量
    trend_component = eemd_data[-1]
    return trend_component




# 判断是否为闰年
def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# 计算每年总天数（平年365天，闰年366天）
def total_days_in_year(year):
    return 366 if is_leap_year(year) else 365

# 计算年平均流量
def calculate_yearly_avg_flow(flow_data):
    # 计算每月天数
    days_in_month = {
        "1": 31, "2": None, "3": 31, "4": 30, "5": 31, "6": 30,
        "7": 31, "8": 31, "9": 30, "10": 31, "11": 30, "12": 31
    }
    yearly_avg_flow = flow_data.copy()
    for year in yearly_avg_flow.index:
        total_days = total_days_in_year(year)
        days_in_month["2"] = 29 if is_leap_year(year) else 28
        yearly_avg_flow.loc[year, '年平均流量'] = sum(
            flow_data.loc[year] * [days_in_month[month] for month in flow_data.columns]
        ) / total_days
    return yearly_avg_flow["年平均流量"].tolist()




if __name__ == '__main__':
    # # 计算年平均流量
    flow_data = pd.read_excel("./数据源/大通站月均流量.xlsx",index_col=0)
    flow_data.columns = [str(i) for i in range(1, 13)]
    yearly_avg_flow_data = calculate_yearly_avg_flow(flow_data)
    print(yearly_avg_flow_data)