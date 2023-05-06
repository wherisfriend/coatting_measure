#-*- coding:utf-8 -*-
#-------------------------------------
# @Author: CSU_赵阳
# @Date: 2023-04-19 21:11:19 
# @Last Modified by:   csu.zhaoyang 
# @Last Modified time: 2023-04-19 21:11:19 
# @Describe: 覆层厚度测量
# ----------------

import time
import os
from PIL import Image,ImageDraw,ImageFont
from PySide2.QtGui import QPixmap
from PySide2.QtCore import QFile, Qt , QDateTime, QTimer
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMessageBox, QFileDialog, QLabel
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import cv2
from binary_kernel import binary
from fun.circle_fun import gravity_center,cal_radius,circle_roughness


class Test:
    def __init__(self) -> None:
        super(Test, self).__init__()

        file = QFile('thickness_Dialog.ui')
        file.open(QFile.ReadOnly)
        file.close()

        self.ui = QUiLoader().load(file)

        # 设定预览框大小为16：9的比例
        self.ui.label.resize(800,450)
        # 选择图片
        self.ui.B1.clicked.connect(self.open_file)
        # 二值化查询
        self.ui.B2.clicked.connect(self.binary_value)
        # 偏圆度测量
        self.ui.B3.clicked.connect(self.roungness_measure)
        
        self.image_path = ''

    # 选择照片
    def open_file(self):
        # QFileDialog().getOpenFileName(self.ui, '选择文件', 'c:/', '*.png')
        # 选择单个文件
        # 重新设置Label大小
        
        file = QFileDialog().getOpenFileName(self.ui, '选择文件','','')
        # 选择多个文件
        # file = QFileDialog().getOpenFileNames(self.ui, '选择文件','','')
        # print(file)
        img_path = str(file[0])

        self.image_path = img_path

        # 获取图片尺寸信息. (1423, 673)
        img_Size = self.get_img_size(img_path)

        # 调整图片预览窗格大小
        self.ui.label.resize(int(450*img_Size[0]/img_Size[1]),450)

        # 适应图框
        self.ui.label.setScaledContents(True)
        self.ui.label.setPixmap(QPixmap(img_path))


    # 图片二值化查询
    def binary_value(self):
        print("二值化")
        if self.image_path == '':
            # 错误对话框
            QMessageBox.critical(self.ui, '输入错误','请先选择图片', QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
            return
        # 启动二值化窗口
        binary(self.image_path)

    # 偏圆度识别
    def roungness_measure(self):
        # threshold = self.ui.threshold.text()
        threshold = int(self.ui.threshold.text())
        if self.image_path == '':
            # 错误对话框
            QMessageBox.critical(self.ui, '输入错误','请先选择图片', QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
            return
        elif threshold == '':
            # 未输入阈值
            QMessageBox.critical(self.ui, '二值化阈值未输入','请输入二值化阈值', QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
            return

        du = math.pi/180
        # 矩阵不省略，显示矩阵详情
        np.set_printoptions(threshold=np.inf)
        # D:/A_GUI_CAD/GUI_table/roundness_measurement/F01_K3_JJ.png
        tmp_name = self.image_path.split('/')
        # F01_K3_JJ.png
        img_Real_name= tmp_name[len(tmp_name)-1]
        # F01_K3_JJ
        img_name = img_Real_name.split('.')[0]
        # print(img_name)

        img = Image.open(self.image_path)
        # 模式L”为灰色图像，它的每个像素用8个bit表示，0表示黑，255表示白，其他数字表示不同的灰度。
        Img = img.convert('L')

        curdir = os.path.abspath(os.curdir) #获取当前工作目录路径
        curdir = curdir.replace('\\' , '/')
        curdir_L = str(curdir + '/output/'+ img_name + "_灰度.png")
        Img.save(curdir_L)

        # 自定义灰度界限，大于这个值为白色，小于这个值为黑色。 125时生成带覆层轮廓的的
        threshold = int(self.ui.threshold.text())
        # threshold =114
        table = []
        for i in range(256):
            if i < threshold:
                table.append(1)
            else:
                table.append(0)
        # 图片二值化
        photo = Img.point(table, '1')
        curdir_L = str(curdir + '/output/'+ img_name + "_二值化.png")
        photo.save(curdir_L)

        # 二值化后转变为矩阵
        arr = np.array(photo)
        # 将true、false转成0和1数组
        arr = arr + 0

        # 输出图片的形心
        X_rows, X_cols = gravity_center(arr)
        print('图形的形心为第{}行,第{}列'.format(X_rows,X_cols))

        # 计算等效半径
        R = cal_radius(arr)
        print('图形的等效半径为{}'.format(R))

        # 输出偏离圆程度
        res =circle_roughness(arr,R)
        print('图形与等效圆的差异度为{}'.format(res))

        # 在截面上画出圆心，等效圆
        img2 = cv2.imread(self.image_path)

        imgWC = cv2.circle(img2,(int(X_cols),int(X_rows)),int(2),(255,0,0),3)
        # imgWC1 = cv2.circle(img2,(int(X_cols),int(X_rows)),int(R),(0,0,255),3)
        ###############################采集内外轮廓点###############################


        # 搜索臂长R
        L_S = int(R*1.3)

        # 覆层极值
        Fu_max = 0
        Fu_min = 9999999999999

        filename = str(curdir + '/output/'+ img_name + "_360度覆层厚度_射线法px.txt")
        File1=open(filename,mode='w')

        Res_Min_Point1 = []
        Res_Min_Point2 = []

        Res_Max_Point1 = []
        Res_Max_Point2 = []
        sum = 0

        # 图片大小
        rows, cols = arr.shape
        # 内轮廓点集
        N_table = []

        # 外轮廓点集
        W_table = []

        # 覆层厚度
        Fu_table = []


        # 射线法，采集内外轮廓点
        for m in range(360):
                
            # sum = sum + 1
            # 标签0
            Point1 = []
            Point2 = []
            tag = 0
            for j in range(L_S):
                Tmp_L_S = L_S - j
                Var_Col = int(X_cols + Tmp_L_S*math.cos(m*du))
                Var_Row = int(X_rows + Tmp_L_S*math.sin(m*du))
                if Var_Row<=0 or Var_Row>=rows or Var_Col<=0 or Var_Col>=cols:
                    continue
                else:
                    if arr[Var_Row][Var_Col]==1 and tag == 0:
                    
                        if len(Point1) == 0:
                            Point1.append(Var_Row)
                            Point1.append(Var_Col)
                            # 添加到外轮廓点集
                            W_table.append(Point1)
                            tag = 1
                        else:
                            Point2.append(Var_Row)
                            Point2.append(Var_Col)

                            # 添加到内轮廓点集
                            N_table.append(Point2)

                            col_diff = Point1[1]-Point2[1]
                            row_diff = Point1[0]-Point2[0]

                            fu_var = math.sqrt(col_diff*col_diff + row_diff*row_diff)

                            # 添加到覆层厚度点集
                            Fu_table.append(fu_var)
                            # print(str(m) +'~~~~~~~' + str(fu_var))

                            File1.writelines(str(fu_var)+'\n')

                            # cv2.line(img2,(Point1[1], Point1[0]), (Point2[1], Point2[0]), (255,0,255),2)

                            if fu_var > Fu_max:
                                Fu_max = fu_var
                                Res_Max_Point1 = Point1
                                Res_Max_Point2 = Point2

                            if fu_var < Fu_min:
                                Fu_min = fu_var
                                Res_Min_Point1 = Point1
                                Res_Min_Point2 = Point2

                            break
                        
                    elif arr[Var_Row][Var_Col]==1 and tag == 1:
                        pass
                    elif arr[Var_Row][Var_Col]==0 and tag == 1:
                        tag = 0
                    else:
                        pass
        
        File1.close()

        # 是否有360个点
        if len(N_table) != 360 or len(W_table) != 360:
            QMessageBox.critical(self.ui, '内外轮廓不连贯','请调整二值化阈值', QMessageBox.Yes|QMessageBox.No, QMessageBox.No)



        # 距离内轮廓最近的外轮廓点
        W_table_Res = []
        # 距离最薄的覆层
        Fu_table_Res = []

        nums = len(N_table)

        # 这里。 最小壁厚没问题，最大壁厚。
        Fu_max_new = Fu_min
        Fu_min_new = Fu_max

        # 最新的极值线条点
        P_new_Min1 = Res_Min_Point1
        P_new_Min2 = Res_Min_Point2
        P_new_Max1 = Res_Max_Point1
        P_new_Max2 = Res_Max_Point2

        filename1 = str(curdir + '/output/'+ img_name + "_360度覆层厚度_优化px.txt")

        File2=open(filename1,mode='w')

        # 开关
        tag = self.ui.CB1.isChecked()
            # 获取状态
        # print(self.ui.CB1.isChecked())

        var = 360

        if tag:
            var = 60

        for i in range(var):
            if tag:
                x = i*6
            else:
                x = i
            P1 = N_table[x]
            fu_tmp = Fu_table[x]
            R_fu = Fu_table[x]

            # 原始对应的外轮廓点
            tmp_P2 = W_table[x]
            for y in range(nums):
                P2 = W_table[y]
                if P2[0]<P1[0]-R_fu or P2[0]>P1[0]+R_fu or P2[1]<P1[1]-R_fu or P2[1]>P1[1]+R_fu:
                    pass
                else:
                    tmp_row_diff = P1[0]-P2[0]
                    tmp_col_diff = P1[1]-P2[1]
                    distance = math.sqrt(tmp_col_diff**2 + tmp_row_diff**2)
                    if distance<fu_tmp:
                        fu_tmp = distance
                        tmp_P2 = P2

            if fu_tmp>Fu_max_new:
                Fu_max_new = fu_tmp
                P_new_Max1=P1
                P_new_Max2 = tmp_P2

            if fu_tmp<Fu_min_new:
                Fu_min_new = fu_tmp
                P_new_Min1=P1
                P_new_Min2 = tmp_P2

            fu_tmp = round(fu_tmp, 2)            
            File2.writelines(str(fu_tmp)+'\n')
            Fu_table_Res.append(float(fu_tmp))
            # 添加到新的外轮廓对应点集
            W_table_Res.append(tmp_P2)
            # 画线,画出所有线条
            cv2.line(img2,(P1[1], P1[0]), (tmp_P2[1], tmp_P2[0]), (255,0,255),2)
        File2.close()

        # print('最小覆层厚度{}px， 最大覆层厚度{}px'.format(Fu_min_new,Fu_max_new))

        MinL = math.sqrt((P_new_Min1[0]-P_new_Min2[0])**2 + (P_new_Min1[1]-P_new_Min2[1])**2)
        MaxL = math.sqrt((P_new_Max1[0]-P_new_Max2[0])**2 + (P_new_Max1[1]-P_new_Max2[1])**2)

        print('最小覆层厚度{}px， 最大覆层厚度{}px'.format(MinL,MaxL))
        # 标记覆层极值
        imgWC2 = cv2.line(img2,(P_new_Min1[1], P_new_Min1[0]), (P_new_Min2[1], P_new_Min2[0]), (0,0,0),5)
        imgWC3 = cv2.line(img2,(P_new_Max1[1], P_new_Max1[0]), (P_new_Max2[1], P_new_Max2[0]), (155,155,0),5)


        
        #########################################绘图##############################
        
        # # 准备数据
        x_data = [u"{}".format(i) for i in range(0, var)]
        y_data = [u"{}".format(i) for i in Fu_table_Res]

        # print(len(x_data),len(y_data))

        plt.figure()
        # # 正确显示中文和负号
        plt.rcParams["font.sans-serif"] = ["SimHei"]
        plt.rcParams["axes.unicode_minus"] = False

        

        # # 刻度间距
        plt.gca().xaxis.set_major_locator(MultipleLocator(20))
        plt.xlim(0,var)
        plt.xticks(rotation=30)

        # # plt.gca().yaxis.set_major_locator(MultipleLocator(2))
        # # plt.ylim(0,36)
        # # plt.yticks(rotation=30)

        # # 折线图
        # # plt.plot(x_data, float(y_data))

        # # 画图，plt.bar()可以画柱状图
        for i in range(len(x_data)):
    	    plt.bar(x_data[i], float(y_data[i]))

            
        # 设置图片名称
        plt.title("360°覆层厚度波动图_px")
        # 设置x轴标签名
        plt.xlabel("角度（°） ")
        # 设置y轴标签名
        plt.ylabel("覆层厚度（px）")
        # 显示
        plt.savefig(fname=str(curdir + '/output/'+ img_name + "_360度覆层厚度波动图_px.png"), dpi=300)
        plt.show()


        # ####################################单位转换################################
        LongLine = float(self.ui.threshold_2.text() )     # 产品规格，外径 mm
        tmp_min_L = 99999
        tmp_max_R = 0
        tmp_min_L_row = 0
        tmp_max_R_row = 0


        # 找到最坐标和最右边点
        for item in W_table:
            if item[1] < tmp_min_L:
                tmp_min_L = item[1]
                tmp_min_L_row = item[0]
    
            if item[1] > tmp_max_R:
                tmp_max_R = item[1]
                tmp_max_R_row = item[0]
        # 直线的像素值
        MAX_Long = (tmp_max_R-tmp_min_L)*(tmp_max_R-tmp_min_L) + (tmp_max_R_row-tmp_min_L_row)*(tmp_max_R_row-tmp_min_L_row)

        MAX_Long = int (math.sqrt(MAX_Long))

        Real_min = LongLine* MinL / MAX_Long
        Real_max = LongLine * MaxL / MAX_Long

        # 画直线
        imgWC4 = cv2.line(img2,(tmp_min_L, tmp_min_L_row), (tmp_max_R, tmp_max_R_row), (255,155,0),3)

        ####################################输出毫米单位的################################
        filename2 = str(curdir + '/output/'+ img_name + "_360度覆层厚度_优化_mm.txt")

        File3=open(filename2,mode='w')

        for item in Fu_table_Res:
            File3.writelines(str(item*LongLine/MAX_Long)+'\n')
        #################################输出毫米单位的柱状图################################
        # # 准备数据
        x_data = [u"{}".format(i) for i in range(0, var)]
        y_data2 = [u"{}".format(i*LongLine/MAX_Long) for i in Fu_table_Res]

        # print(len(x_data),len(y_data))

        plt.figure()
        # # 正确显示中文和负号
        plt.rcParams["font.sans-serif"] = ["SimHei"]
        plt.rcParams["axes.unicode_minus"] = False

        

        # # 刻度间距
        plt.gca().xaxis.set_major_locator(MultipleLocator(20))
        plt.xlim(0,var)
        plt.xticks(rotation=30)

        # # plt.gca().yaxis.set_major_locator(MultipleLocator(2))
        # # plt.ylim(0,36)
        # # plt.yticks(rotation=30)

        # # 折线图
        # # plt.plot(x_data, float(y_data))

        # # 画图，plt.bar()可以画柱状图
        for i in range(len(x_data)):
    	    plt.bar(x_data[i], float(y_data2[i]))

            
        # 设置图片名称
        plt.title("360°覆层厚度波动图_mm")
        # 设置x轴标签名
        plt.xlabel("角度（°） ")
        # 设置y轴标签名
        plt.ylabel("覆层厚度（mm）")
        # 显示
        plt.savefig(fname=str(curdir + '/output/'+ img_name + "_360度覆层厚度波动图_mm.png"), dpi=300)
        plt.show()


        ####################################输出文本################################

        str_txt1 = str("最小覆层厚度{:.4f}px; 转换为毫米：{:.4f}mm".format(MinL, Real_min))
        str_txt2 = str("最大覆层厚度{:.4f}px; 转换为毫米: {:.4f}mm".format(MaxL, Real_max))
        # str_txt1 = str("最小覆层厚度{:.4f}px;".format(MinL))
        # str_txt2 = str("最大覆层厚度{:.4f}px;".format(MaxL))

        #导入字体文件
        fontpath = "simsun.ttc"
        #设置字体的颜色
        b,g,r,a = 0,0,255,0
        #设置字体大小
        font = ImageFont.truetype(fontpath,20)
        #将numpy array的图片格式转为PIL的图片格式
        img_pil = Image.fromarray(img2)
        #创建画板
        draw = ImageDraw.Draw(img_pil)
        #在图片上绘制中文
        draw.text((5,30),str_txt1,font=font,fill=(0,0,0,a))
        draw.text((5,60),str_txt2,font=font,fill=(155,155,0,a))

        #将图片转为numpy array的数据格式
        img3 = np.array(img_pil)

        #保存图片
        cv2.imwrite(curdir + '/output/'+ img_name + "_result.png",img3)
        cv2.imshow('Image With Circle',img3)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    # 获得图片的尺寸信息
    def get_img_size(self, file_path):
        # file_path = 'C:/Users/admin/Pictures/scence/1.jpg'
        img = Image.open(file_path)
        imgSize = img.size  #大小/尺寸
        w = img.width       #图片的宽
        h = img.height      #图片的高
        f = img.format      #图像格式
        return imgSize

    
if __name__ == '__main__':
    app = QApplication([])
    window = Test()
    window.ui.show()
    app.exec_()
