import os.path
import sys
from libs.pascalVocIO import PascalVocWriter
from base64 import b64encode, b64decode


class LabelFileError(Exception):
    pass


class LabelFile(object):
    # It might be changed as window creates
    suffix = '.lif'

    def __init__(self, filename=None):
        self.shapes = ()
        self.imagePath = None
        self.imageData = None
        if filename is not None:
            self.load(filename)

    def savePascalVocFormat(
            self,
            savefilename,
            image_size,
            shapes,
            imagePath=None,
            databaseSrc=None,
            shape_type_='RECT'):
        imgFolderPath = os.path.dirname(imagePath)  # 返回文件路径的目录
        imgFolderName = os.path.split(imgFolderPath)[-1]  #
        imgFileName = os.path.basename(imagePath)  # 获得文件名，包括后缀
        imgFileNameWithoutExt = os.path.splitext(imgFileName)[0]  # 获取文件名（包括后缀）文件名
        print('imgaeFolderPath:', imgFolderPath)
        print('imgaeFolderName:', imgFolderName)
        print('imgFileName:', imgFileName)
        print(' imgFileNameWithoutExt:', imgFileNameWithoutExt)

        # img = cv2.imread(imagePath)
        writer = PascalVocWriter(
            imgFolderName,
            imgFileNameWithoutExt,
            image_size,
            localImgPath=imagePath,
            shape_type=shape_type_)
        bSave = False
        for shape in shapes:
            points = shape['points']
            label = shape['label']
            if shape['shape_type'] == 0:
                # 检测模式
                # 根据点来创建一个bndbox
                bndbox = LabelFile.convertPoints2BndBox(points)
                writer.addBndBox(bndbox[0], bndbox[1], bndbox[2], bndbox[3], label, shape['difficult'])
            if shape['shape_type'] == 1:
                # 分割模式
                # 添加分割点
                writer.addPolygon(points, label, instance_id=shape['instance_id'], ignore=shape['difficult'])
            bSave = True
            print('label savefilename:', savefilename)

        if bSave:
            writer.save(targetFile=savefilename)  # 这里存储
        return

    @staticmethod
    def isLabelFile(filename):
        fileSuffix = os.path.splitext(filename)[1].lower()
        return fileSuffix == LabelFile.suffix

    @staticmethod
    def convertPoints2BndBox(points):

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

        # Martin Kersner, 2015/11/12
        # 0-valued coordinates of BB caused an error while
        # training faster-rcnn object detector.
        if (xmin < 1):
            xmin = 1

        if (ymin < 1):
            ymin = 1

        return (int(xmin), int(ymin), int(xmax), int(ymax))
