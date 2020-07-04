import sys
from xml.etree.ElementTree import Element, ElementTree
from xml.dom.minidom import parse
from lxml import etree
import os
class Point_Xml_Writer():
    def __init__(self, filepath):
        self.filepath = filepath
        self.visible_list=[]
    def addpoint(self,points,cover):#对整体的保存
        tree = ElementTree()
        tree.parse(self.filepath)
        root = tree.getroot()
        cover_list=cover
        print('points',points)
        print("cover list",cover_list)
        # try:
        for i,object_iter in enumerate(tree.findall('object')):
            if i in range(len(points)):
                if len(points[i])>0:
                    print("rect dex,len(points)",i,len(points[i]))
                    element = Element('point')
                    # keypoints 子结点
                    keypoints = Element('keypoints')
                    keypoints.text = str(self.convert_point(points[i]))
                    # points_num 子结点
                    visible = Element('visible')
                    self.analy_visible(self.convert_point(points[i]),cover_list[i])
                    visible.text = str(self.visible_list)
                    element.append(keypoints)
                    element.append(visible)
                    object_iter.append(element)
                    self.visible_list=[]#写完一次注意清空
            else:
                pass
        tree.write(os.path.splitext(self.filepath)[0]+'_point.xml', encoding='utf-8', xml_declaration=True)


        # except IndexError:
        #     pass
    def addpoint_single(self,points,n,cover):#对单个的保存

        if len(points)>0:
            print("n",n)
            tree = ElementTree()
            tree.parse(self.filepath)
            root = tree.getroot()
            cover_list=cover
            element = Element('point')
            keypoints = Element('keypoints')
            keypoints.text = str(self.convert_point(points[0]))
            visible = Element('visible')
            print("cover",cover_list)
            self.analy_visible(self.convert_point(points[0]),cover_list)
            visible.text = str(self.visible_list)
            element.append(keypoints)
            element.append(visible)
            tree.findall('object')[n].append(element)
            tree.write(os.path.splitext(self.filepath)[0] + '_point.xml', encoding='utf-8', xml_declaration=True)


    def convert_point(self,points):

        a = points
        b = []
        for i in a:
            for ii in i.strip('[').strip(']').strip().split(','):
                b.append(int(float(ii)))
        return b
    def analy_visible(self,points,cover_list):
        num=len(points)//2
        print("num",num)
        print('points',points)
        print("cover_list",cover_list)
        for i in range(num):
            if points[2 * i] == 0 and points[2 * i + 1] == 0:
                self.visible_list.append(0)
            elif i in range(len(cover_list)):
                if cover_list[i]==1:
                    self.visible_list.append(1)
                else:
                    self.visible_list.append(2)
            else:
                self.visible_list.append(2)
        print("visible_list_11111",self.visible_list)

class Point_Xml_Reader():
    def __init__(self, filepath):
        self.filepath = filepath
    def readpoints(self):
        xml_corner=[]
        point_list=[]
        point_list_list=[]
        visible_list=[]
        xml_corner = []
        b = []
        c = []
        if os.path.exists(self.filepath):
            tree = etree.parse(self.filepath)
            # get bbox
            for subobj in tree.findall("object"):
                if subobj.findall('point'):
                    print(subobj)
                    for points in subobj.findall('point'):  # 获取元素的内容
                        for corner in points.getchildren():  # 便利point元素下的子元素
                            xml_corner.append(corner)  # string类型
                    for i in xml_corner:
                        for ii in i.text.strip('[').strip(']').strip().split(','):
                            if ii:
                                b.append(int(ii))
                        c.append(b)
                        b = []
                    for i in range(len(c)//2):
                        point_list.append(c[i*2])
                        visible_list.append(c[2*i+1])
                else:
                    point_list.append([])
                    visible_list.append([])

                xml_corner = []
                b = []
                c = []
        else:
            pass
        return point_list,visible_list
    def point_to_points(self,point_list):#[365, 230, 344, 199]->[[365, 230], [344, 199]]
        point_list_list=[]
        list=[]
        for pp in point_list:
            for i in range(len(pp)//2):
                list.append([pp[2*i],pp[2*i+1]])
            print('list')
            point_list_list.append(list)
            list=[]
        return point_list_list

b=Point_Xml_Reader(r'E:\Annotation\person\3_point.xml')
q=b.readpoints()
print(q)