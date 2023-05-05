请使用虚拟机运行AAAAcad_gui文件




报错,请看下链接
启动虚拟机教程, 第一次启动虚拟机，可能会报错，按下链接处理
cd cad_GUI_Venv/Scrpits/
运行: ./activate启动虚拟机
https://blog.csdn.net/weixin_45465367/article/details/128522361

选用虚拟机运行程序

​1、建议配合虚拟环境，一起打包

python3 -m venv thickness_Venv




```text
source cad_GUI/bin/activate
deactivate







1、exe打包

pip insatll pyinstaller

注意事项：



# 多文件
pyinstaller -D -i panda.ico cad_gui.py
```

deactivate

https://blog.csdn.net/weixin_45465367/article/details/128522361



echo "# cad_gui" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/wherisfriend/cad_gui.git
git push -u origin main