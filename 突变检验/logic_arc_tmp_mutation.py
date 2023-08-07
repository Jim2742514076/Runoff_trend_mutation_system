# -*-coding = utf-8 -*-
# @Time : 2023/8/6 14:58
# @Author : 万锦
# @File : logic_arc_tmp_mutation.py
# @Softwore : PyCharm

import numpy as np
from scipy.stats import linregress
import pandas as pd
from pymannkendall import original_test
import matplotlib.pyplot as plt
from PyEMD import EEMD


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
#mk突变分析
def Kendall_change_point_detection(index,inputdata):
    inputdata = np.array(inputdata)
    n=inputdata.shape[0]
    Sk = [0]
    UFk = [0]
    s =  0
    Exp_value = [0]
    Var_value = [0]
    for i in range(1,n):
        for j in range(i):
            if inputdata[i] > inputdata[j]:
                s = s+1
            else:
                s = s+0
        Sk.append(s)
        Exp_value.append((i+1)*(i+2)/4 )                     # Sk[i]的均值
        Var_value.append((i+1)*i*(2*(i+1)+5)/72 )            # Sk[i]的方差
        UFk.append((Sk[i]-Exp_value[i])/np.sqrt(Var_value[i]))
    Sk2 = [0]
    UBk = [0]
    UBk2 = [0]
    # s归0
    s2 =  0
    Exp_value2 = [0]
    Var_value2 = [0]
    # 按时间序列逆转样本y
    inputdataT = list(reversed(inputdata))
    for i in range(1,n):
        for j in range(i):
            if inputdataT[i] > inputdataT[j]:
                s2 = s2+1
            else:
                s2 = s2+0
        Sk2.append(s2)
        Exp_value2.append((i+1)*(i+2)/4 )                     # Sk[i]的均值
        Var_value2.append((i+1)*i*(2*(i+1)+5)/72 )            # Sk[i]的方差
        UBk.append((Sk2[i]-Exp_value2[i])/np.sqrt(Var_value2[i]))
        UBk2.append(-UBk[i])
    UBkT = list(reversed(UBk2))
    diff = np.array(UFk) - np.array(UBkT)
    K    = list()
    # 找出交叉点
    for k in range(1,n):
        if diff[k-1]*diff[k]<0:
            K.append(k)

    return K,UFk,UBkT

#有序聚类突变分析
def compute_sse(data, tau):
    n = len(data)
    mean_x = np.mean(data)

    sse1 = np.sum((data[:tau] - np.mean(data[:tau])) ** 2)
    sse2 = np.sum((data[tau:] - np.mean(data[tau:])) ** 2)

    return sse1 + sse2

#搜索突变点
def find_change_point(data):
    min_sse = float('inf')
    best_tau = None
    sse_values = []

    for tau in range(1, len(data)):
        sse = compute_sse(data, tau)
        sse_values.append(sse)
        if sse < min_sse:
            min_sse = sse
            best_tau = tau

    return best_tau, min_sse, sse_values

#Pettitt突变点检测
def Pettitt_change_point_detection(inputdata):
    inputdata = np.array(inputdata)
    n         = inputdata.shape[0]
    k = range(n)
    inputdataT = pd.Series(inputdata)
    r = inputdataT.rank()
    Uk = [2*np.sum(r[0:x])-x*(n + 1) for x in k]
    Uka = list(np.abs(Uk))
    U = np.max(Uka)
    K = Uka.index(U)
    pvalue         = 2 * np.exp((-6 * (U**2))/(n**3 + n**2))
    if pvalue <= 0.05:
        change_point_desc = '显著'
    else:
        change_point_desc = '不显著'
    Pettitt_result = {'突变点位置':K,'突变程度':change_point_desc}
    return Pettitt_result,Uka


