import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from xml.dom import minidom
from lxml import etree
import os


class PascalVocWriter:

    def __init__(
            self,
            foldername,  # 文件夹
            filename,  # 文件名
            imgSize,
            databaseSrc='Unknown',
            localImgPath=None,
            shape_type=None):
        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.boxlist = []
        self.localImgPath = localImgPath
        self.shape_type = shape_type

    def prettify(self, elem):  # 修饰
        """
            Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf8')  # 生成一个字符串来表示xml的element
        # rough_string = ElementTree.tostring(elem)#从字符串中生成xml树
        root = etree.fromstring(rough_string)  # lxml下的fromstring
        return etree.tostring(root, pretty_print=True)

    def genXML(self):
        """
            Return XML root
        """
        # Check conditions
        '''
        if self.filename is None or \
                        self.foldername is None or \
                        self.imgSize is None or \
                        len(self.boxlist) <= 0:
        '''
        if self.filename is None or \
                len(self.boxlist) <= 0:
            return None

        top = Element('annotation')
        folder = SubElement(top, 'folder')
        folder.text = self.foldername

        filename = SubElement(top, 'filename')
        filename.text = self.filename

        localImgPath = SubElement(top, 'path')
        self.localImgPath = self.localImgPath.split('/')[-1]
        localImgPath.text = self.localImgPath

        source = SubElement(top, 'source')
        database = SubElement(source, 'database')
        database.text = self.databaseSrc

        if self.imgSize:
            size_part = SubElement(top, 'size')
            width = SubElement(size_part, 'width')
            height = SubElement(size_part, 'height')
            depth = SubElement(size_part, 'depth')
            width.text = str(self.imgSize[1])
            height.text = str(self.imgSize[0])
            if len(self.imgSize) == 3:
                depth.text = str(self.imgSize[2])
            else:
                depth.text = '1'

        segmented = SubElement(top, 'segmented')
        segmented.text = '0'
        shape_type = SubElement(top, 'shape_type')
        shape_type.text = self.shape_type
        return top

    def addBndBox(self, xmin, ymin, xmax, ymax, name, ignore):
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        bndbox['name'] = name
        bndbox['difficult'] = ignore
        self.boxlist.append(bndbox)

    def addPolygon(self, shape, name, instance_id, ignore):
        polygon = {}
        i = 0
        for point in shape:
            polygon[i] = point
            i = i + 1
        polygon['name'] = name
        polygon['point_num'] = str(len(shape))
        polygon['instance_id'] = instance_id
        polygon['difficult'] = ignore
        self.boxlist.append(polygon)

    def appendObjects(self, top):
        for each_object in self.boxlist:
            object_item = SubElement(top, 'object')
            if each_object['name']:
                name = SubElement(object_item, 'name')
                name.text = str(each_object['name'])
            pose = SubElement(object_item, 'pose')
            pose.text = "Unspecified"
            if 'instance_id' in each_object.keys():
                instance_id = SubElement(object_item, 'instance_id')
                instance_id.text = str(each_object['instance_id'])
            truncated = SubElement(object_item, 'truncated')
            truncated.text = '0'
            if 'difficult' in each_object.keys():
                difficult = SubElement(object_item, 'difficult')
                difficult.text = str(each_object['difficult'])
            if self.shape_type == 'RECT':
                bndbox = SubElement(object_item, 'bndbox')
                xmin = SubElement(bndbox, 'xmin')
                xmin.text = str(each_object['xmin'])
                ymin = SubElement(bndbox, 'ymin')
                ymin.text = str(each_object['ymin'])
                xmax = SubElement(bndbox, 'xmax')
                xmax.text = str(each_object['xmax'])
                ymax = SubElement(bndbox, 'ymax')
                ymax.text = str(each_object['ymax'])
            elif self.shape_type == 'POLYGON':
                polygon = SubElement(object_item, 'polygon')
                for i in range(int(each_object['point_num'])):
                    point = SubElement(polygon, 'point' + str(i))
                    point.text = str(
                        int(each_object[i][0])) + ',' + str(int(each_object[i][1]))

    def save(self, targetFile=None):
        # 这里生成了整个xml
        root = self.genXML()
        self.appendObjects(root)
        out_file = None
        if targetFile is None:
            out_file = open(self.filename + '.xml', 'w')
        else:
            print('correct path：', targetFile.split('/' + self.filename + '.xml')[0])
            try:
                out_file = open(str(targetFile), 'w')
            except FileNotFoundError:
                print('error tackle:', targetFile.split('/' + self.filename + '.xml')[0])
                if not os.path.exists(targetFile.split(self.filename + '.xml')[0]):
                    os.makedirs(targetFile.split('/' + self.filename + '.xml')[0])  # 创建文件夹的层级路径
                out_file = open(str(targetFile), 'w')

        out_file.write(str(self.prettify(root).decode()))
        out_file.close()


class PascalVocReader:

    def __init__(self, filepath):
        # shapes type:
        ## [label, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color，shape_type,instace_id]
        self.shapes = []
        self.filepath = filepath
        self.shape_type = None
        self.image_size = []
        self.parseXML()

    def getShapes(self):
        return self.shapes

    def getShapeType(self):
        return self.shape_type

    def addPolygonShape(self, label, points, instance_id=0, ignore=0):
        points = [(point[0], point[1]) for point in points]
        self.shapes.append((label, points, None, None, 1, instance_id, ignore))

    def get_img_size(self):
        if self.image_size:
            return self.image_size

    def addShape(self, label, rect, instance_id=0, ignore=0):
        xmin = rect[0]
        ymin = rect[1]
        xmax = rect[2]
        ymax = rect[3]
        points = [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]
        self.shapes.append((label, points, None, None, 0, instance_id, ignore))

    def parseXML(self):
        assert self.filepath.endswith('.xml'), "Unsupport file format"
        parser = etree.XMLParser(encoding='utf-8')
        try:
            xmltree = ElementTree.parse(self.filepath, parser=parser).getroot()  # parser=parser
            # xmltree = ElementTree.parse('E:\LabelImgTool-master_7\LabelImgTool-master\example_picture\\1.xml', parser=parser).getroot()
            filename = xmltree.find('filename').text
            if xmltree.find('shape_type') is not None:
                self.shape_type = xmltree.find('shape_type').text
            else:
                self.shape_type = 'RECT'
            self.image_size.append(int(xmltree.find('size').find('width').text))
            self.image_size.append(int(xmltree.find('size').find('height').text))
            if self.shape_type == 'RECT':
                for object_iter in xmltree.findall('object'):
                    rects = []
                    bndbox = object_iter.find("bndbox")
                    rects.append([int(it.text) for it in bndbox])
                    label = object_iter.find('name').text
                    ignore = int(object_iter.find('difficult').text)
                    for rect in rects:
                        self.addShape(label, rect, ignore=ignore)
                return True
            elif self.shape_type == 'POLYGON':
                instance_id = 0
                for object_iter in xmltree.findall('object'):
                    points = []
                    polygons = object_iter.find("polygon")
                    label = object_iter.find('name').text
                    ignore = int(object_iter.find('difficult').text)
                    for point in polygons:
                        point = point.text.split(',')
                        point = [int(dot) for dot in point]
                        points.append(point)
                    if object_iter.find('instance_id') is not None:
                        instance_id = int(object_iter.find('instance_id').text)
                    self.addPolygonShape(label, points, instance_id, ignore=ignore)
            else:
                print('unsupportable shape type')
        except etree.XMLSyntaxError:  # xml文件出错
            pass


# tempParseReader = PascalVocReader('test.xml')
# print tempParseReader.getShapes()
"""
# Test
tmp = PascalVocWriter('temp','test', (10,20,3))
tmp.addBndBox(10,10,20,30,'chair')
tmp.addBndBox(1,1,600,600,'car')
tmp.save()
"""
