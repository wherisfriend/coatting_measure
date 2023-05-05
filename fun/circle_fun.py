#-------------------------------------
# @Author: CSU_赵阳
# @Date: 2023-03-21 14:42:34 
# @Last Modified by:   csu.zhaoyang 
# @Last Modified time: 2023-03-21 14:42:34 
#-------------------------------------import numpy as np
import math
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageFont

# 矩阵不省略，显示矩阵详情
np.set_printoptions(threshold=np.inf)


# 计算图像的形心
def gravity_center(array):
    """计算重心，array的元素都是1或者0, 且只有一个连通域，计算1部分的重心"""
    rows, cols = array.shape
    sumx = 0
    sumy = 0
    for x in range(rows):
        for y in range(cols):
            sumx += array[x, y] * x
            sumy += array[x, y] * y
    center_x = sumx / array.sum()
    center_y = sumy / array.sum()
    return center_x, center_y


# 计算等效半径
def cal_radius(array):
    rows, cols = array.shape
    center_x, center_y = gravity_center(array)
    J = 0.0
    A = array.sum()
    for x in range(rows):
        for y in range(cols):
            if array[x, y]:
                d_square = (x - center_x) ** 2 + (y - center_y) ** 2
                J += d_square
    radius = math.sqrt(2 * J / A)
    return radius



# 计算圆度
def circle_roughness(array, radius):
    rows, cols = array.shape
    center_x, center_y = gravity_center(array)
    sum_ = 0.0
    sum_area = 0
    for x in range(rows):
        for y in range(cols):
            d_square = (x - center_x) ** 2 + (y - center_y) ** 2
            d = math.sqrt(d_square)
            if (d < radius and array[x, y] == 0) or (d > radius and array[x, y] == 1):
                # 凹坑 inside circle or  凸起 outside circle
                sum_ += (radius - d) ** 2
                sum_area += 1
                # print(x, y, array[x, y], d)
    h = math.sqrt(sum_ / sum_area)  # 平均起伏
    return h / radius  # 越小越圆，无量纲。


# 输出结果图片 
def out_pic(imgname,X_rows, X_cols,res,R):
    # 在截面上画出等效圆
    img2 = cv2.imread(imgname)

    imgWC = cv2.circle(img2,(int(X_cols),int(X_rows)),int(R),(0,0,255))

    str_txt = str("图形偏离真圆程度为{:.4f}".format(res))

    #导入字体文件
    fontpath = "simsun.ttc"
    #设置字体的颜色
    b,g,r,a = 0,255,0,0
    #设置字体大小
    font = ImageFont.truetype(fontpath,15)
    #将numpy array的图片格式转为PIL的图片格式
    img_pil = Image.fromarray(img2)
    #创建画板
    draw = ImageDraw.Draw(img_pil)
    #在图片上绘制中文
    draw.text((10,150),str_txt,font=font,fill=(b,g,r,a))
    #将图片转为numpy array的数据格式
    img3 = np.array(img_pil)

    #保存图片
    cv2.imwrite("K3_res.jpg",img3)

    cv2.imshow('Image With Circle',img3)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

