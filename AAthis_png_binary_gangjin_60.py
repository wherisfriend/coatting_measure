#-------------------------------------
# @Author: CSU_赵阳
# @Date: 2023-03-22 12:13:30 
# @Last Modified by:   csu.zhaoyang 
# @Last Modified time: 2023-03-22 12:13:30 
# @Describe： 在内轮廓上，某一点为圆心，找距离外轮廓最近的点。 最新的
#-------------------------------------
from PIL import Image,ImageDraw,ImageFont
import numpy as np
import math
import cv2

from fun.circle_fun import gravity_center,cal_radius,circle_roughness,out_pic

du = math.pi/180

# 矩阵不省略，显示矩阵详情
np.set_printoptions(threshold=np.inf)

# 图片的名称
imgname = str('HHYY_K1.png')
# 横直线的长度,毫米单位mm
LongLine = 250

tmp_name = imgname.split('.')

img_Real_name= tmp_name[0]

print(img_Real_name)

img = Image.open(imgname)
 
# 模式L”为灰色图像，它的每个像素用8个bit表示，0表示黑，255表示白，其他数字表示不同的灰度。
Img = img.convert('L')
Img.save(img_Real_name + "_灰度.png")
 
# 自定义灰度界限，大于这个值为白色，小于这个值为黑色。 125时生成带覆层轮廓的的
threshold = 125
table = []
for i in range(256):
    if i < threshold:
        table.append(1)
    else:
        table.append(0)
# 图片二值化
photo = Img.point(table, '1')
photo.save(img_Real_name + "_二值化.png")

# 二值化后转变为矩阵
arr = np.array(photo)
# 将true、false转成0和1数组
arr = arr + 0

# 自定义灰度界限，大于这个值为白色，小于这个值为黑色。 125时生成带覆层轮廓的的
threshold = 240
table = []
for i in range(256):
    if i < threshold:
        table.append(1)
    else:
        table.append(0)
# 图片二值化
photo = Img.point(table, '1')
photo.save(img_Real_name + "_区域划分.png")

# 二值化后转变为矩阵
arr2 = np.array(photo)
# 将true、false转成0和1数组
arr2 = arr2 + 0


# 输出图片的形心
X_rows, X_cols = gravity_center(arr2)
print('图形的形心为第{}行,第{}列'.format(X_rows,X_cols))

# 计算等效半径
R = cal_radius(arr2)
# print('图形的等效半径为{}'.format(R))

# 输出偏离圆程度
# res =circle_roughness(arr2,R)
# print('图形与等效圆的差异度为{}'.format(res))


# 覆层极值
Fu_max = 0
Fu_min = 9999999999999

X_rows = int(X_rows)
X_cols = int(X_cols)

# 搜索臂长R
L_S = int(R*1.3)

Res_Min_Point1 = []
Res_Min_Point2 = []

Res_Max_Point1 = []
Res_Max_Point2 = []

File1=open(img_Real_name + '_360_res.txt',mode='w')

sum = 0
# 在截面上画出圆心，等效圆
img2 = cv2.imread(imgname)

# 图片大小
rows, cols = arr2.shape

# 内轮廓点集
N_table = []

# 外轮过点集
W_table = []

# 覆层厚度
Fu_table = []

# 采集内外轮廓点。以及覆层厚度
for m in range(0,360):
    sum = sum + 1
    # 标签0
    Point1 = []
    Point2 = []
    tag = 0
    for j in range(L_S):
        Tmp_L_S = L_S - j
        Var_Col = X_cols + int(Tmp_L_S*math.cos(m*du))
        Var_Row = X_rows + int(Tmp_L_S*math.sin(m*du))
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

# 距离内轮廓最近的外轮廓点
W_table_Res = []
# 距离最薄的覆层
Fu_table_Res = []


nums = len(N_table)
# print(nums)
# # 找到更薄的覆层
# for x in N_table:
#     for y in W_table:

# 这里。 最小壁厚没问题，最大壁厚。
Fu_max_new = Fu_min
Fu_min_new = Fu_max

# 最新的极值线条点
P_new_Min1 = Res_Min_Point1
P_new_Min2 = Res_Min_Point2
P_new_Max1 = Res_Max_Point1
P_new_Max2 = Res_Max_Point2

File2=open(img_Real_name + '_60_res.txt',mode='w')

for i in range(60):
    x = i*6
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
    
    File2.writelines(str(fu_tmp)+'\n')
    Fu_table_Res.append(fu_tmp)
    # 添加到新的外轮廓对应点集
    W_table_Res.append(tmp_P2)
    # 画线,画出所有线条
    cv2.line(img2,(P1[1], P1[0]), (tmp_P2[1], tmp_P2[0]), (255,0,255),2)
File2.close()

            
print('最小覆层厚度{}px， 最大覆层厚度{}px'.format(Fu_min_new,Fu_max_new))

print(str(P_new_Min1) + ',,,,' + str(P_new_Min2))
print(str(P_new_Max1) + ',,,,' + str(P_new_Max2))


imgWC = cv2.circle(img2,(int(X_cols),int(X_rows)),int(2),(255,0,0),3)
# imgWC1 = cv2.circle(img2,(int(X_cols),int(X_rows)),int(R),(0,0,255),1)

MinL = math.sqrt((P_new_Min1[0]-P_new_Min2[0])**2 + (P_new_Min1[1]-P_new_Min2[1])**2)
MaxL = math.sqrt((P_new_Max1[0]-P_new_Max2[0])**2 + (P_new_Max1[1]-P_new_Max2[1])**2)



print('最小覆层厚度{}px， 最大覆层厚度{}px'.format(MinL,MaxL))

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

print("最左边{0}，{1} px".format(tmp_min_L, tmp_max_R_row))
print("最右边{0},{1} px".format(tmp_max_R, tmp_max_R_row))
print("直线长度：{0} px".format(MAX_Long))

imgWC2 = cv2.line(img2,(P_new_Min1[1], P_new_Min1[0]), (P_new_Min2[1], P_new_Min2[0]), (0,0,0),3)
imgWC3 = cv2.line(img2,(P_new_Max1[1], P_new_Max1[0]), (P_new_Max2[1], P_new_Max2[0]), (255,255,0),3)

# 画直线
imgWC4 = cv2.line(img2,(tmp_min_L, tmp_min_L_row), (tmp_max_R, tmp_max_R_row), (255,155,0),3)

# imgWC3 = cv2.line(img2,(Res_Max_Point1[1],Res_Max_Point1[0]), (Res_Max_Point2[1], Res_Max_Point2[0]), (255,255,0),3)


# str_txt = str("图形偏离真圆程度为{:.4f}".format(res))
str_txt1 = str("最小覆层厚度{:.4f}px; 转换为毫米：{:.4f}mm".format(MinL, Real_min))
str_txt2 = str("最大覆层厚度{:.4f}px; 转换为毫米: {:.4f}mm".format(MaxL, Real_max))

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
# draw.text((10,150),str_txt,font=font,fill=(b,g,r,a))

draw.text((10,50),str_txt1,font=font,fill=(0,0,0,a))

draw.text((10,90),str_txt2,font=font,fill=(255,255,0,a))

#将图片转为numpy array的数据格式
img3 = np.array(img_pil)

#保存图片
cv2.imwrite(img_Real_name + "_结果.png",img3)

cv2.imshow('Image With Circle',img3)
cv2.waitKey(0)
cv2.destroyAllWindows()




