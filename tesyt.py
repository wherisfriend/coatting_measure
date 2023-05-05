str = 'D:/A_GUI_CAD/GUI_table/roundness_measurement/F01_K3_JJ.png'
tmp_name = str.split('/')

# print(len(tmp_name))
# print(tmp_name[len(tmp_name)-1])


# 获取当前路径
import os

print (os.getcwd()) #获取当前工作目录路径
print (os.path.abspath('.'))#获取当前工作目录路径
# print (os.path.abspath('test.txt')) #获取当前目录文件下的工作目录路径
print (os.path.abspath('..')) #获取当前工作的父目录 ！注意是父目录路径
print (os.path.abspath(os.curdir)) #获取当前工作目录路径

cur = os.path.abspath(os.curdir)

cur = cur.replace('\\' , '/')

print(cur)

