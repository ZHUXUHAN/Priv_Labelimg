import json
import xml.etree.ElementTree as ET
from lxml import etree
import numpy as np
class Voc_To_Coco():
    def __init__(self, _voc_xml_path, _save_json_path):
        self._voc_xml_path = _voc_xml_path
        self._save_json_path = _save_json_path

        self.images = []
        self.categories = [{
            "skeleton": [
                [
                    16,
                    14
                ],
                [
                    14,
                    12
                ],
                [
                    17,
                    15
                ],
                [
                    15,
                    13
                ],
                [
                    12,
                    13
                ],
                [
                    6,
                    12
                ],
                [
                    7,
                    13
                ],
                [
                    6,
                    7
                ],
                [
                    6,
                    8
                ],
                [
                    7,
                    9
                ],
                [
                    8,
                    10
                ],
                [
                    9,
                    11
                ],
                [
                    2,
                    3
                ],
                [
                    1,
                    2
                ],
                [
                    1,
                    3
                ],
                [
                    2,
                    4
                ],
                [
                    3,
                    5
                ],
                [
                    4,
                    6
                ],
                [
                    5,
                    7
                ]
            ],
            "supercategory": "person",
            "keypoints": [
                "nose",
                "left_eye",
                "right_eye",
                "left_ear",
                "right_ear",
                "left_shoulder",
                "right_shoulder",
                "left_elbow",
                "right_elbow",
                "left_wrist",
                "right_wrist",
                "left_hip",
                "right_hip",
                "left_knee",
                "right_knee",
                "left_ankle",
                "right_ankle"
            ],
            "parsing": [
                "background",
                "Hat",
                "Hair",
                "Glove",
                "Sunglasses",
                "UpperClothes",
                "Dress",
                "Coat",
                "Socks",
                "Pants",
                "Torso-skin",
                "Scarf",
                "Skirt",
                "Face",
                "Left-arm",
                "Right-arm",
                "Left-leg",
                "Right-leg",
                "Left-shoe",
                "Right-shoe"
            ],
            "id": 1,
            "name": "person"
        }]
        self.annotations = []
        self.bbox=[]
        self.points=[]
        self.vis=[]
        self.keypoints=[]
    def processing_xml(self):
        tree = ET.parse(self._voc_xml_path)
        #images part
        filename_node= tree.findall('filename')
        filename=filename_node[0].text
        size=tree.findall('size')
        height=size[0].findall('height')[0].text
        width=size[0].findall('width')[0].text
        id=0
        image = {'height': float(height), 'width': float(width), 'id': id, 'file_name': filename+'.jpg'}
        self.images.append(image)
        #categories
        #annotations
        object = tree.findall('object')

        for i,obj in enumerate(object):
            bbox = obj.find('bndbox')
            label = obj.find('name').text.lower().strip()
            x1 = np.maximum(0.0, float(bbox.find('xmin').text))
            y1 = np.maximum(0.0, float(bbox.find('ymin').text))

            x2 = np.minimum(float(width) - 1.0, float(bbox.find('xmax').text))
            y2 = np.minimum(float(height) - 1.0, float(bbox.find('ymax').text))
            # rectangle = [x1, y1, x2, y2]
            bbox = [x1, y1, x2 - x1 + 1, y2 - y1 + 1]  # [x,y,w,h]
            area = (x2 - x1 + 1) * (y2 - y1 + 1)

            points = obj.findall('point')
            for m, point in enumerate(points):
                keypoint = point.find('keypoints').text
                vis = point.find('visible').text
                self.points.append(keypoint)
                self.vis.append(vis)


            self.keypoints=self.processing_points(self.points,self.vis)
            print("self.points", self.keypoints)
            print(i)

            annotation = {'segmentation': [], 'iscrowd': 0, 'area': area, 'image_id': id,
                          'bbox': bbox,
                          'category_id': 1, 'id': id,'keypoints':self.keypoints[i]}
            self.annotations.append(annotation)
            id+=1

    def processing_points(self,points,vis):
        s=[]
        ss=[]
        sss=[]
        v=[]
        point_list=[]
        for i,point in enumerate(points):
            for ii in point.strip('[').strip(']').strip().split(','):
                s.append(int(ii.strip()))
            ss.append(s)
            s=[]
        for viss in vis:
            for visss in viss.strip('[').strip(']').strip().split(','):
                v.append(int(visss))

        for i,w in enumerate(ss):
            for q in range(len(w)//2):
                point_list.append(w[2*q])
                point_list.append(w[2*q+1])
                point_list.append(v[i*17+q])
            sss.append(point_list)
            point_list=[]

        return sss

    def save_json(self):
        data_coco = {'images': self.images, 'categories': self.categories, 'annotations': self.annotations}
        json.dump(data_coco, open(self._save_json_path, 'w'))

vv=Voc_To_Coco('E:/Annotation/person/3_point.xml','E:/Priv-lab1-2018-9-17-master/3_point.json')
vv.processing_xml()
vv.save_json()

