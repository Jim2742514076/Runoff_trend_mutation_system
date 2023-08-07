# -*-coding = utf-8 -*-
# @Time : 2023/8/2 15:40
# @Author : 万锦
# @File : run.py
# @Softwore : PyCharm


from PyQt5.QtGui import *
from qfluentwidgets import MessageBox
# from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
import sys
import os
import time
import pandas as pd
from logic_arc_tmp_trend import calculate_yearly_avg_flow,linear_regression,emd_trend,mk_test,cumulative_anomaly
from matplotlib import pyplot as plt

from trend_analysis import Ui_MainWindow
class Form_waterinf(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(Form_waterinf, self).__init__()
        self.setupUi(self)
        self.setObjectName("trend_analysis")
        self.handlebutton()
        self.ininitialize()
        self.year_runoff = []
        self.time_series = []

    def ininitialize(self):
        self.PushButton_2.setEnabled(False)
        self.PushButton_3.setEnabled(False)
        self.PushButton_4.setEnabled(False)
        self.PushButton_5.setEnabled(False)

    def handlebutton(self):
        self.PushButton.clicked.connect(self.add_data)
        self.PushButton.clicked.connect(self.deal_button)
        self.PushButton_2.clicked.connect(self.linear_logic)
        self.PushButton_3.clicked.connect(self.mk_test_qt)
        self.PushButton_4.clicked.connect(self.emd_analysis)
        self.PushButton_5.clicked.connect(self.contive_analysis)
        self.PushButton_6.clicked.connect(self.call_author)

    #解除按钮限制
    def deal_button(self):
        self.PushButton_2.setEnabled(True)
        self.PushButton_3.setEnabled(True)
        self.PushButton_4.setEnabled(True)
        self.PushButton_5.setEnabled(True)

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

    #逻辑回归
    def linear_logic(self):
        slope, intercept, r_value, p_value, std_err = linear_regression(self.time_series,self.year_runoff)

        #文本显示
        show_slope = f"斜率（趋势）：{slope}"
        show_intercept = f"截距：{intercept}"
        show_r_value = f"相关系数 R 值：{r_value}"
        show_p_value = f"p 值：{p_value}"
        show_std_err = f"标准误差：{std_err}"
        show_inf = [show_slope,show_intercept,show_r_value,show_p_value,show_std_err]
        text = "\n".join(show_inf)
        self.TextEdit.setText(text)

        #保存绘图
        path = QFileDialog.getSaveFileName(self,"保存文件","./",("图片(*.png)"))
        # print(path)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        y = np.polyfit(self.time_series, self.year_runoff, 1)
        plt.plot(self.time_series, self.year_runoff,  marker='o', label='年平均流量')
        plt.plot(self.time_series, np.polyval(y, self.time_series),  linestyle="--", label='趋势线')
        plt.legend()
        plt.title('线性回归趋势图')
        plt.ylabel("流量($m^3/s$)")
        if path:
            plt.savefig(path[0])
            plt.close('all')
            self.label.setPixmap(QPixmap(path[0]))

        tmp = pd.DataFrame({"年份":self.time_series,"流量":self.year_runoff,"趋势":np.polyval(y, self.time_series)})

        #保存数据
        path = QFileDialog.getSaveFileName(self, "保存文件", "./", ("结果(*.xlsx)"))
        if path:
            tmp.to_excel(path[0])

    #mk检验
    def mk_test_qt(self):
        result = mk_test(self.year_runoff)
        # 输出MK检验结果
        z = f"Z值：{result.z}"
        p = f"p值：{result.p}"
        if result.trend == "increasing":
            t = "趋势：上升"
        elif result.trend == "decreasing":
            t = "趋势：下降"
        else:
            t = "趋势：无趋势"
        if result.p < 0.05:
            judge = "在显著性水平0.05下，拒绝原假设，认为存在趋势。"
        else:
            judge = "在显著性水平0.05下，接受原假设，认为不存在趋势。"
        inf = [z,p,t,judge]
        text = "\n".join(inf)
        self.TextEdit.setText(text)
        self.label.setPixmap(QPixmap("./icons/三峡集团.png"))


    #emd分析
    def emd_analysis(self):
        runoff_data = np.array(self.year_runoff)
        trend_component = emd_trend(runoff_data)
        # 绘制趋势图
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(trend_component, label='趋势分量')
        plt.xlabel('时间')
        plt.ylabel('EMD趋势项')
        plt.title('EMD趋势分析')
        # 保存绘图
        path = QFileDialog.getSaveFileName(self, "保存文件", "./", ("图片(*.png)"))
        if path:
            plt.savefig(path[0])
            plt.close('all')
            self.label.setPixmap(QPixmap(path[0]))
            self.TextEdit.setText("右图显示为emd分解后的剩余项，该项可以表示序列整体趋势")

        tmp = pd.DataFrame({"年份": self.time_series,"emd趋势项": trend_component})

        # 保存数据
        path = QFileDialog.getSaveFileName(self, "保存文件", "./", ("结果(*.xlsx)"))
        if path:
            tmp.to_excel(path[0])

    #累积距平分析
    def contive_analysis(self):
        cumulative_departure_data = cumulative_anomaly(self.year_runoff)
        # 绘制距平图
        # 绘制累积距平序列图
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.plot(cumulative_departure_data)
        plt.xlabel('时间')
        plt.ylabel('累积距平')
        plt.title('累积距平法趋势分析')
        plt.grid(True)
        # 保存绘图
        path = QFileDialog.getSaveFileName(self, "保存文件", "./", ("图片(*.png)"))
        if path:
            plt.savefig(path[0])
            plt.close('all')
            self.label.setPixmap(QPixmap(path[0]))
            self.TextEdit.setText("右图显示为累积距平法趋势分析图")

        tmp = pd.DataFrame({"年份": self.time_series, "累积距平": cumulative_departure_data})

        # 保存数据
        path = QFileDialog.getSaveFileName(self, "保存文件", "./", ("结果(*.xlsx)"))
        if path:
            tmp.to_excel(path[0])


def main():
    app = QApplication(sys.argv)
    mainwindow = Form_waterinf()
    mainwindow.setWindowTitle("年径流趋势分析系统")
    mainwindow.setWindowIcon(QIcon("./icons/三峡.jpg"))
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()