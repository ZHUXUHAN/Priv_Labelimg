# Priv_Labelimg
这个是个包含六种模式，六种功能的视觉图像数据标注工具。
六个功能分别是：分类、分割、检测框、画刷以及基于人体关键点和人手脸。

需要安装：
python3/2 (更建议在3下使用)

pyqt5

opencv

qdarkstyle

requests

运行方式：

一、源码运行

python labelimg.py

二、windows平台下exe可执行文件运行

只需要下载Priv-LabelImg_1.0，其中有个exe文件，直接运行即可。


人体关键点功能

使用方式

使用过程截图

![image](https://github.com/ZHUXUHAN/Priv_Labelimg/blob/master/example.png)

如何转换为coco数据集json格式，lib文件夹下有个voc_to_coco的py文件，修正其中路径即可。

如果想可视化所标注的关键点，可参考本人的另外一个工程COCOAPI_Visualition

注意：本工程仍在添加功能，尚只有本人个人维护，由于在做其他的project，本工程的代码版本不稳定，上诉的六个功能现在的使用情况尚好，如本project无法正常使用，可以联系我，我将提供最新稳定标注软件版本。

Note: If you want to use keypoint mode, you can just reference the Priv-Labelimg-v2.1-Instructions.pdf.

注意：如果你想使用关键点模式，你可以参照Priv-Labelimg-v2.1-Instructions.pdf。
