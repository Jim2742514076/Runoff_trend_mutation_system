# -*-coding = utf-8 -*-
# @Time : 2023/8/5 9:03
# @Author : 万锦
# @File : run_mutation.py
# @Softwore : PyCharm

from PyQt5.QtGui import *
from qfluentwidgets import MessageBox
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
import sys
import os
import time
import pandas as pd
from logic_arc_tmp_mutation import (calculate_yearly_avg_flow,Kendall_change_point_detection,Pettitt_change_point_detection,find_change_point,
                      )
from matplotlib import pyplot as plt

from mutation_analysis import Ui_MainWindow
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
class Form_waterinf(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(Form_waterinf, self).__init__()
        self.setupUi(self)
        self.setObjectName("mutation_analysis")
        self.handlebutton()
        self.ininitialize()
        self.year_runoff = []
        self.time_series = []

    def ininitialize(self):
        self.PushButton_2.setEnabled(False)
        self.PushButton_3.setEnabled(False)
        self.PushButton_4.setEnabled(False)
        # self.PushButton_5.setEnabled(False)

    def handlebutton(self):
        self.PushButton.clicked.connect(self.add_data)
        self.PushButton.clicked.connect(self.deal_button)
        self.PushButton_2.clicked.connect(self.mk_test_mutation)
        self.PushButton_3.clicked.connect(self.pettitt_test)
        self.PushButton_4.clicked.connect(self.agglomerative)
        # self.PushButton_5.clicked.connect(self.contive_analysis)
        self.PushButton_6.clicked.connect(self.call_author)

    #解除按钮限制
    def deal_button(self):
        self.PushButton_2.setEnabled(True)
        self.PushButton_3.setEnabled(True)
        self.PushButton_4.setEnabled(True)
        # self.PushButton_5.setEnabled(True)

    #联系作者
    def call_author(self):
        title = '联系作者'
        content = """wanjinhhu@gmail.com"""
        # w = MessageDialog(title, content, self)   # Win10 style message box
        w = MessageBox(title, content, self)
        if w.exec():
           pass
        else:
            pass



    #添加数据
    def add_data(self):
        fname, _ = QFileDialog.getOpenFileName(self, "打开文件", '.', '数据文件(*.xlsx)')
        if fname:
            df = pd.read_excel(fname,index_col=0)
            df.columns = [str(i) for i in range(1, 13)]
            self.year_runoff = calculate_yearly_avg_flow(df)
            data = df.values
            #表格加载数据
            # 设置行列，设置表头
            tmp = ["一月", "二月", "三月", "四月","五月", "六月", "七月", "八月","九月", "十月", "十一月", "十二月"]
            self.time_series = df.index.values
            tmp2 = [str(_) for _ in df.index.tolist()]
            self.TableWidget.setRowCount(len(data))
            self.TableWidget.setColumnCount(len(data[0]))
            self.TableWidget.setHorizontalHeaderLabels(tmp)
            self.TableWidget.setVerticalHeaderLabels(tmp2)
            # 表格加载内容
            for row, form in enumerate(data):
                for column, item in enumerate(form):
                    self.TableWidget.setItem(row, column, QTableWidgetItem(str(item)))

    #mk检验
    def mk_test_mutation(self):
        k,UFk,UBkT = Kendall_change_point_detection(self.time_series,self.year_runoff)
        year = self.time_series[k]
        # 做突变检测图时，使用UFk和UBkT
        # plt.figure(figsize=(10, 5))
        plt.figure(figsize=(6, 4))
        plt.plot(self.time_series, UFk, label='UFk')  # UFk
        plt.plot(self.time_series, UBkT, label='UBk')  # UBk
        plt.ylabel('UFk-UBk')
        x_lim = plt.xlim()
        plt.plot(x_lim, [-1.96, -1.96], 'm--', color='r')
        plt.plot(x_lim, [0, 0], 'm--')
        plt.plot(x_lim, [+1.96, +1.96], 'm--', color='r')
        plt.legend(loc=2)  # 图例
        # 保存绘图
        path = QFileDialog.getSaveFileName(self, "保存文件", "./", ("图片(*.png)"))
        if path:
            plt.savefig(path[0])
            plt.close('all')
            self.label.setPixmap(QPixmap(path[0]))
        year_tmp = [str(_) for _ in year]
        tmp ="\n".join(year_tmp)
        text = f"""
                           判别规则：MK突变点检测根据UFk-UBk在置信区间内的交点判定\n  
                           突变年份为:\n{tmp}  
                       """

        self.TextEdit.setText(text)
        tmp = pd.DataFrame({"年份": self.time_series, "UFk": UFk, "UBk": UBkT})

        # 保存数据
        path = QFileDialog.getSaveFileName(self, "保存文件", "./", ("结果(*.xlsx)"))
        if path:
            tmp.to_excel(path[0])

    #Pettitt突变点检测
    def pettitt_test(self):
        Pettitt_result,Uka = Pettitt_change_point_detection(self.year_runoff)

        #绘图
        plt.figure(figsize=(6, 4))
        plt.plot(self.time_series,Uka)
        plt.ylabel("Uka")
        plt.title('Pettitt突变检验')
        # 保存绘图
        path = QFileDialog.getSaveFileName(self, "保存文件", "./", ("图片(*.png)"))
        if path:
            plt.savefig(path[0])
            plt.close('all')
            self.label.setPixmap(QPixmap(path[0]))
        text = f"""
                           判别规则：Pettitt突变点检测根据Uka的最大值进行突变点判定\n
                           突变年份为:{self.time_series[Pettitt_result['突变点位置']]}，\n突变程度{Pettitt_result['突变程度']}
                       """

        self.TextEdit.setText(text)
        tmp = pd.DataFrame({"年份": self.time_series, "Uka": Uka})

        # 保存数据
        path = QFileDialog.getSaveFileName(self, "保存文件", "./", ("结果(*.xlsx)"))
        if path:
            tmp.to_excel(path[0])

    #有序聚类突变分析
    def agglomerative(self):

        best_tau, min_sse, sse_values = find_change_point(self.year_runoff)


        # 绘制离差平方和折线图
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.figure(figsize=(6, 4))
        plt.plot(self.time_series[1:], sse_values, marker='o', linestyle='-', color='b')
        plt.xlabel('τ')
        plt.ylabel('离差平方和')
        plt.title('离差平方和随τ变化的折线图')
        plt.grid(True)
        # 保存绘图
        path = QFileDialog.getSaveFileName(self, "保存文件", "./", ("图片(*.png)"))
        if path:
            plt.savefig(path[0])
            plt.close('all')
            self.label.setPixmap(QPixmap(path[0]))

        text = f"""
                           判别规则：有序聚类突变分析根据离差平方和最小值进行突变点判定\n
                           注意事项：τ为分割点，因此起始点是从第二年开始的\n
                           最小离差平方和：{min_sse}\n
                           最优τ值（可能的突变点位置）：{self.time_series[best_tau+1]}
                       """
        self.TextEdit.setText(text)
        tmp = pd.DataFrame({"年份": self.time_series[1:], "离差平方和": sse_values})

        # 保存数据
        path = QFileDialog.getSaveFileName(self, "保存文件", "./", ("结果(*.xlsx)"))
        if path:
            tmp.to_excel(path[0])


def main():
    app = QApplication(sys.argv)
    mainwindow = Form_waterinf()
    mainwindow.setWindowTitle("年径流突变分析系统")
    mainwindow.setWindowIcon(QIcon("./icons/三峡.ico"))
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()