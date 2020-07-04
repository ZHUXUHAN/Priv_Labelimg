import sys
from xml.etree.ElementTree import Element, ElementTree
from xml.dom.minidom import parse
from lxml import etree
import os
class Parse_Xml_Writer():
    def __init__(self, filepath):
        self.filepath = filepath
        self.shapes_list=[]
        self.bbox_list=[]
        self.label=None

    def addbboxs(self,shapes):#对整体的保存
        tree = ElementTree()
        tree.parse(self.filepath)
        root = tree.getroot()
        self.shapes_list=shapes
        print('len',len(shapes))
        # self.analysis_bboxes()
        # try:
        for i,object_iter in enumerate(tree.findall('object')):
            if i in range(len(shapes)):

                # element.text='shapes'
                if len(shapes[i])>0:
                    for i,shape in enumerate(shapes[i]):
                        self.analysis_bboxes(shape)
                        print(self.bbox_list)
                        #shapes根节点
                        element = Element('shapes')
                        # label 子结点
                        label = Element('label')
                        label.text = str(self.label)
                        # x min  ymin  xmax ymax子结点
                        bbox_element= Element('parse_bbox')
                        xmin = Element('xmin')
                        xmin.text = str(self.bbox_list[0])
                        ymin = Element('ymin')
                        ymin.text = str(self.bbox_list[1])
                        xmax = Element('xmax')
                        xmax.text = str(self.bbox_list[2])
                        ymax = Element('ymax')
                        ymax.text = str(self.bbox_list[3])

                        element.append(label)
                        element.append(bbox_element)
                        bbox_element.append(xmin)
                        bbox_element.append(ymin)
                        bbox_element.append(xmax)
                        bbox_element.append(ymax)
                        object_iter.append(element)
            else:
                pass
        tree.write(os.path.splitext(self.filepath)[0]+'_parse.xml', encoding='utf-8', xml_declaration=True)

    def analysis_bboxes(self,shape):
        points = shape['points']
        self.bbox_list=self.convertPoints2BndBox(points)
        self.label=shape['label']
    def convertPoints2BndBox(self,points):
        xmin = sys.maxsize
        ymin = sys.maxsize
        xmax = -sys.maxsize
        ymax = -sys.maxsize
        for p in points:
            x = p[0]
            y = p[1]
            xmin = min(x, xmin)
            ymin = min(y, ymin)
            xmax = max(x, xmax)
            ymax = max(y, ymax)
        if (xmin < 1):
            xmin = 1
        if (ymin < 1):
            ymin = 1

        return (int(xmin), int(ymin), int(xmax), int(ymax))

class Parse_Xml_Reader():
    def __init__(self, filepath):
        self.filepath = filepath
        self.shapes={}
        self.single_shapes=[]
    def getshapes(self):
        self.readparses()
        id_list=[]
        shapes_list=[]
        if len(self.single_shapes)>0:
            for i, shape in enumerate(self.single_shapes):
                id_list.append(shape[5])
            for i in range(max(id_list)+1):
                for id, shape in enumerate(self.single_shapes):
                    if shape[5]==i:
                        shapes_list.append(self.single_shapes[id])
                        self.shapes[i]=shapes_list
                shapes_list=[]
            print(self.shapes)
        else:
            return None
        return self.shapes


    def readparses(self):
        rect=[]
        rects=[]
        label=[]
        assert self.filepath.endswith('.xml'), "Unsupport file format"
        if os.path.exists(self.filepath):
            tree = etree.parse(self.filepath)
            for id,object_iter in enumerate(tree.findall('object')):
                for _,parse in enumerate(object_iter.findall('shapes')):  # 获取元素的内容
                    # rect.append([int(it.text) for it in  parse.findall("parse_bbox")])
                    label.append(parse.find("label").text)
                    print("labellabel", label)
                    for it in parse.find("parse_bbox"):
                        rect.append(it.text)
                    rects.append(rect)
                    rect=[]
                self.addShape(label, rects, id)

                rects=[]
                label=[]
        else:
            pass

    def addShape(self, label, rects,instance_id = 0):
        for i,rect in enumerate(rects):
            xmin = int(rect[0])
            ymin = int(rect[1])
            xmax = int(rect[2])
            ymax = int(rect[3])
            points = [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]
            self.single_shapes.append((label[i], points, None, None, 0, instance_id))



# a=Parse_Xml_Writer(r'C:\Users\旭涵\Desktop\5.xml')
# a.addbboxs([[(),(),()],[(),(),()]])

# b=Parse_Xml_Reader('E:/Annotation/person/3_parse.xml')
# b.getshapes()
# print(b.single_shapes)

