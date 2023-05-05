#-------------------------------------
# @Author: CSU_赵阳
# @Date: 2023-04-20 08:32:56 
# @Last Modified by:   csu.zhaoyang 
# @Last Modified time: 2023-04-20 08:32:56 
# @Describe： 二值化进度条
#-------------------------------------#coding:utf-8
import cv2
import os

img = []

# 修改类型
def on_type(a):

    model_type = cv2.getTrackbarPos("type", "binary_image")
    value = cv2.getTrackbarPos("value", "binary_image")
    ret, dst = cv2.threshold(img, value, 255, model_type)
    cv2.imshow("binary_image", dst)


# 修改二值化阈值
def on_value(a):

    model_type = cv2.getTrackbarPos("type", "binary_image")
    value = cv2.getTrackbarPos("value", "binary_image")
    ret, dst = cv2.threshold(img, value, 255, model_type)
    cv2.imshow("binary_image", dst)


def binary(png_name):


    # 1.导入图片
    global img
    
    path = os.getcwd()

    # print("python27 {}/binary_kernel.py".format(path))

    # pic_name = str(path) + "\binary_special_PNG.png"
    
    # img = cv2.imread("D:\\abaqus_2021_tmp\\A_cloud_Abaqus\\binary\\binary_special.png", cv2.IMREAD_GRAYSCALE)

    img = cv2.imread(str(png_name), cv2.IMREAD_GRAYSCALE)



    # 2.显示图片 创建图片窗体
    cv2.namedWindow("binary_image")
    cv2.imshow("binary_image", img)

    # 3.创建滑动条
    cv2.createTrackbar("type", "binary_image", 0, 4, on_type)
    cv2.createTrackbar("value", "binary_image", 0, 255, on_value)

    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    
    # 测试的图片名称,需在本件夹中
    png_name = "F01_K2_NJ.png"
    binary(png_name)

