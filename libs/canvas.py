from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os

from libs.shape import Shape
from libs.lib import distance
from libs.predefined_points import Predefined_Points
from math import sqrt
import numpy as np
import random
CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT = Qt.PointingHandCursor
CURSOR_DRAW = Qt.CrossCursor
CURSOR_MOVE = Qt.ClosedHandCursor
CURSOR_GRAB = Qt.OpenHandCursor

cur_pth=os.getcwd()

class Canvas(QWidget):
    zoomRequest = pyqtSignal(int)#zoom需求的自定义信号
    scrollRequest = pyqtSignal(int, int)#scroll的自定义信号
    newShape = pyqtSignal()
    selectionChanged = pyqtSignal(bool)
    shapeMoved = pyqtSignal()
    Point_Change=pyqtSignal(int,bool,list)
    Point_Vis_Change=pyqtSignal(int)
    Point_Error=pyqtSignal(bool,int)
    Parse_Error=pyqtSignal(bool,int)
    drawingPolygon = pyqtSignal(bool)
    CREATE, EDIT = range(2)
    RECT_SHAPE, POLYGON_SHAPE = range(2)#矩形，多边形

    epsilon = 11.0

    def __init__(self, *args, **kwargs):
        super(Canvas, self).__init__(*args, **kwargs)#*args将输入的参数存放为元组，**kwargs将输入的参数存放为字典
        # Initialise local state.
        PP = Predefined_Points()
        self.shape_type = self.POLYGON_SHAPE
        self.image=QImage()
        self.brush_point = None
        self.task_mode = 3
        self.erase_mode = False
        self.current_brush_path = None
        self.mask_Image = None
        self.brush_color =QColor(255,0,0,255)
        self.brush_size = 10
        self.brush = QPainter();
        self.mode = self.EDIT
        self.shapes = []
        self.current = None
        self.selectedShape = None  # save the selected shape here
        self.selectedShapeCopy = None
        self.lineColor = QColor(0, 0, 255)
        self.line = Shape(line_color=self.lineColor)
        self.prevPoint = QPointF()
        self.offsets = QPointF(), QPointF()
        self.scale = 1.2
        self.bg_image = QImage()
        self.visible = {}

        self._hideBackround = False
        self.hideBackround = False
        self.hShape = None
        self.hVertex = None
        self._painter = QPainter(self)
        self.font_size = 50
        self._cursor = CURSOR_DEFAULT
        # Menus:
        self.menus = (QMenu(), QMenu())
        # Set widget options.
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)
        ##point
        self.point_point=None
        self.point_point_list=[]
        self.point_point_list_tmp=[]
        self.point_dex=None
        self.point_color=[QColor(r ,g ,b ) for r in [0,160,120,30,40] for g in [0,160,120,30,90] for b in [0,160,120,30]]
        self.point_move=None
        self.point_path= None
        self.point_selecteditem=None
        self.point_delete=False
        self.point_modified=False
        self.point_shape={}
        self.point_link=PP.define_points_links()
        self.point_num =max(np.array(self.point_link)[:,1])
        # self.point_visible = {i:True for i in range(len(self.point_link))}
        self.point_visible={i:True for i in range(self.point_num+1)}
        self.point_cover = {i: 2 for i in range(self.point_num )}
        self.point_deletedid=[]
        self.point_ids=[]
        self.point_all_deleted=False
        self.point_save=[]
        self.point_link_save=[]
        self.point_rect=[]
        self.point_rects=[]
        self.point_rects_index=0
        self.point_next_rect=False
        self.point_shape={}
        self.point_changed=False
        self.point_cover_change=False
        self.point_cover_change_dex=0
        self.point_cover_dict={}
        #parse
        self.parse_rects={}
        self.parse_rects_index=0
        self.parse_rects_num=0
        self.parse_shapes={}

        self.xuxian=None
        self.start=False
        self.started=False

    def set_shape_type(self, type):
        if type == 0:
            self.shape_type = self.RECT_SHAPE
            self.line.set_shape_type(type)
            return True
        elif type == 1:
            self.shape_type = self.POLYGON_SHAPE
            self.line.set_shape_type(type)
            return True
        else:
            print ("not support the shape type: " + str(type))
            return False
    def enterEvent(self, ev):
        self.overrideCursor(self._cursor)
    def get_mask_image(self):
        return self.mask_pixmap
    def leaveEvent(self, ev):
        self.restoreCursor()
    def focusOutEvent(self, ev):
        self.restoreCursor()
    def isVisible(self, shape):
        return self.visible.get(shape, True)
    def drawing(self):
        return self.mode == self.CREATE
    def editing(self):
        return self.mode == self.EDIT
    def setEditing(self, value=True):
        self.mode = self.EDIT if value else self.CREATE
        if not value:  # Create
            self.unHighlight()
            self.deSelectShape()
    def unHighlight(self):
        if self.hShape:
            self.hShape.highlightClear()
        self.hVertex = self.hShape = None
    def selectedVertex(self):
        return self.hVertex is not None
    def mouseMoveEvent(self, ev):#这个函数是最重要的函数
        """Update line with last point and current coordinates."""
        pos = self.transformPos(ev.pos())#点一下return一个pos
        self.restoreCursor()#鼠标图标

        if not self.outOfPixmap(pos) and  self.start and not self.started and (self.task_mode ==0 or self.task_mode==5):
            self.xuxian = pos
            self.repaint()


        if self.task_mode == 3:
            self.brush_point = pos
            if Qt.LeftButton & ev.buttons():#左鼠标点击
                if self.outOfPixmap(pos):#超出图像范围
                    return
                if not self.current_brush_path:
                    self.current_brush_path = QPainterPath()
                    self.current_brush_path.moveTo(pos)
                else:
                    self.current_brush_path.lineTo(pos)
            self.repaint()
            return
        if self.task_mode==4:
            self.point_point = pos
            if len(self.point_rects) == 1:
                self.draw_point_single_img(self.point_point_list,0)
            else:
                if self.point_rects_index>0:
                    self.draw_point_single_img(self.point_point_list,self.point_rects_index)
            #     else:
            #         self.draw_point_single_img(self.point_point_list, self.point_rects_index)

            for i, p in enumerate(self.point_point_list):
                if p and distance(p - pos) <= 5 :
                    self.point_dex=i+1#这里加一的目的是为了绘制的时候 不会出现id=0的情况，因此self.point_dex最小为1 而不是0
                    self.Point_Change.emit(i, True, [])  # point change  发射信号
            self.repaint()
            return

        # Polygon drawing.
        if self.drawing():
            self.start=True
            self.overrideCursor(CURSOR_DRAW)
            if self.current:
                color = self.lineColor
                if self.outOfPixmap(pos):
                    # Don't allow the user to draw outside the pixmap.
                    # Project the point to the pixmap's edges.
                    pos = self.intersectionPoint(self.current[-1], pos)
                elif len(self.current) > 1 and self.closeEnough(pos, self.current[0]):
                    # Attract line to starting point and colorise to alert the
                    # user:
                    pos = self.current[0]
                    color = self.current.line_color
                    self.overrideCursor(CURSOR_POINT)
                    self.current.highlightVertex(0, Shape.NEAR_VERTEX)
                #add xu xian
                #

                self.line[1] = pos
                self.line.line_color = color
                self.repaint()
                self.current.highlightClear()
            return
        # Polygon copy moving.
        if Qt.RightButton & ev.buttons():
            if self.selectedShapeCopy and self.prevPoint:
                self.overrideCursor(CURSOR_MOVE)
                self.boundedMoveShape(self.selectedShapeCopy, pos)
                self.repaint()
            elif self.selectedShape:
                self.selectedShapeCopy = self.selectedShape.copy()
                self.repaint()
            return

        # Polygon/Vertex moving.
        if Qt.LeftButton & ev.buttons():
            if self.selectedVertex():
                self.boundedMoveVertex(pos)
                self.shapeMoved.emit()
                self.repaint()
            elif self.selectedShape and self.prevPoint:
                self.overrideCursor(CURSOR_MOVE)
                self.boundedMoveShape(self.selectedShape, pos)
                self.shapeMoved.emit()
                self.repaint()
            return


        # Just hovering over the canvas, 2 posibilities:
        # - Highlight shapes
        # - Highlight vertex
        # Update shape/vertex fill and tooltip value accordingly.
        self.setToolTip("Image")
        for shape in reversed([s for s in self.shapes if self.isVisible(s)]):
            # Look for a nearby vertex to highlight. If that fails,
            # check if we happen to be inside a shape.
            index = shape.nearestVertex(pos, self.epsilon)
            if index is not None:
                if self.selectedVertex():
                    self.hShape.highlightClear()
                self.hVertex, self.hShape = index, shape
                shape.highlightVertex(index, shape.MOVE_VERTEX)
                self.overrideCursor(CURSOR_POINT)
                self.setToolTip("Click & drag to move point")#移动点
                self.setStatusTip(self.toolTip())
                self.update()
                break
            elif shape.containsPoint(pos):
                if self.selectedVertex():
                    self.hShape.highlightClear()
                self.hVertex, self.hShape = None, shape
                self.setToolTip(
                    "Click & drag to move shape '%s'" %
                    shape.label)
                self.setStatusTip(self.toolTip())
                self.overrideCursor(CURSOR_GRAB)
                self.update()
                break
        else:  # Nothing found, clear highlights, reset state.
            if self.hShape:
                self.hShape.highlightClear()
                self.update()
            self.hVertex, self.hShape = None, None
    def mousePressEvent(self, ev):
        mods=ev.modifiers()
        pos = self.transformPos(ev.pos())
        task_mode=self.task_mode
        if self.start==True and task_mode==0:
            self.started=True
            self.xuxian=None

        if ev.button() == Qt.LeftButton:
            if self.drawing():#
                if self.shape_type == self.POLYGON_SHAPE and self.current:
                    self.current.addPoint(self.line[1])
                    self.line[0] = self.current[-1]
                    if self.current.isClosed():
                        self.finalise()


                elif self.shape_type == self.RECT_SHAPE and self.current and self.current.reachMaxPoints() is False:

                    if self.task_mode == 5 and len(self.shapes)>=3:
                        self.current=None
                        self.xuxian = None
                        self.start = False
                        self.started = False
                        QMessageBox.about(self, "About", self.tr(
                            '<p><b>%s</b></p>%s <p>%s</p>' % ('注意标注已经为', str(3) + '个', '只可修改')))
                        return

                        # self.repaint()
                    initPos = self.current[0]
                    minX = initPos.x()
                    minY = initPos.y()
                    targetPos = self.line[1]
                    maxX = targetPos.x()
                    maxY = targetPos.y()
                    self.current.addPoint(QPointF(minX, maxY))
                    self.current.addPoint(targetPos)
                    self.current.addPoint(QPointF(maxX, minY))
                    self.current.addPoint(initPos)
                    self.line[0] = self.current[-1]
                    if self.current.isClosed():
                        self.finalise()

                elif not self.outOfPixmap(pos):
                    self.current = Shape(shape_type=self.shape_type)
                    self.current.addPoint(pos)
                    self.line.points = [pos, pos]
                    self.setHiding()
                    self.drawingPolygon.emit(True)
                    self.update()

            elif self.task_mode == 4:
                self.point_changed=True

                if self.point_modified :
                    self.point_point_list[self.point_modified-1]=pos
                    self.point_modified = False
                    self.repaint()
                else:
                    distances=[]
                    self.point_point_list.append(pos)
                    # if not len(self.point_point_list)>self.point_num :
                    if Qt.LeftButton & ev.buttons():  # 左鼠标点击
                        if self.outOfPixmap(pos):  # 超出图像范围
                            return
                        elif len(self.point_point_list)>1:
                            if self.point_point_list[-1] and self.point_point_list[-2]:
                                if distance(self.point_point_list[-1]-self.point_point_list[-2])<=5:
                                    self.point_move=True
                                    del self.point_point_list[-1]
                            for i,p in enumerate(self.point_point_list[:-2]):
                                if p:
                                    distances.append(distance(p - pos))
                            distances.sort()
                            print('distances')
                            if len(distances)>=1:
                                if distances[0] <=5:#注意 一次只能删除一个点
                                    if distances[0]<=5:
                                        self.point_move=True#这里给出可移动的指令
                                    del self.point_point_list[-1]
                        if self.point_move:
                            self.point_point=pos
                    self.overrideCursor(Qt.CrossCursor)
                    self.repaint()
                    return
            else:
                self.selectShapePoint(pos)
                self.prevPoint = pos
                self.repaint()

        elif ev.button() == Qt.RightButton and self.editing():
            self.selectShapePoint(pos)
            self.prevPoint = pos
            self.repaint()#这里只是传点吧
    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.RightButton:
            menu = self.menus[bool(self.selectedShapeCopy)]
            self.restoreCursor()
            if not menu.exec_(self.mapToGlobal(ev.pos()))\
               and self.selectedShapeCopy:
                # Cancel the move by deleting the shadow copy.
                self.selectedShapeCopy = None
                self.repaint()
        elif ev.button() == Qt.LeftButton and self.selectedShape:
            self.overrideCursor(CURSOR_GRAB)
        elif ev.button() == Qt.LeftButton and self.task_mode ==3 and self.current_brush_path:
            self.current_brush_path = None
        elif ev.button() == Qt.LeftButton and self.task_mode == 4 and self.point_move:#删除点
            # del self.point_point_list[self.point_dex]
            self.point_changed=True
            self.point_point_list[self.point_dex-1]=self.point_point
            self.point_move=False
            self.repaint()
    def endMove(self, copy=False):
        assert self.selectedShape and self.selectedShapeCopy
        shape = self.selectedShapeCopy
        print("end move")
        if copy:
            self.shapes.append(shape)
            self.selectedShape.selected = False
            self.selectedShape = shape
            self.repaint()
        else:
            shape.label = self.selectedShape.label
            shape.ignore = self.selectedShape.ignore
            self.deleteSelected()
            self.shapes.append(shape)
        self.selectedShapeCopy = None
    def hideBackroundShapes(self, value):
        self.hideBackround = value
        if self.selectedShape:
            # Only hide other shapes if there is a current selection.
            # Otherwise the user will not be able to select a shape.
            self.setHiding(True)
            self.repaint()
    def setHiding(self, enable=True):
        self._hideBackround = self.hideBackround if enable else False
    def canCloseShape(self):
        return self.drawing() and self.current and len(self.current) > 2
    def mouseDoubleClickEvent(self, ev):
        # We need at least 4 points here, since the mousePress handler
        # adds an extra one before this handler is called.
        if self.canCloseShape() and len(self.current) > 3:
            self.current.popPoint()
            self.finalise()
    def selectShape(self, shape):
        self.deSelectShape()
        shape.selected = True
        self.selectedShape = shape
        self.setHiding()
        self.selectionChanged.emit(True)
        self.update()

    def selectShapePoint(self, point):
        """Select the first shape created which contains this point."""
        self.deSelectShape()
        if self.selectedVertex():  # A vertex is marked for selection.
            index, shape = self.hVertex, self.hShape
            shape.highlightVertex(index, shape.MOVE_VERTEX)
            return
        for shape in reversed(self.shapes):
            if self.isVisible(shape) and shape.containsPoint(point):
                shape.selected = True
                self.selectedShape = shape
                self.calculateOffsets(shape, point)
                self.setHiding()
                self.selectionChanged.emit(True)
                return
    def calculateOffsets(self, shape, point):
        rect = shape.boundingRect()
        x1 = rect.x() - point.x()
        y1 = rect.y() - point.y()
        x2 = (rect.x() + rect.width()) - point.x()
        y2 = (rect.y() + rect.height()) - point.y()
        self.offsets = QPointF(x1, y1), QPointF(x2, y2)
    def boundedMoveVertex(self, pos):

        index, shape = self.hVertex, self.hShape
        point = shape[index]


        if self.outOfPixmap(pos):
            pos = self.intersectionPoint(point, pos)

        shiftPos = pos - point#point 是之前画好的点 pos为当前的点
        shape.moveVertexBy(index, shiftPos)


        if self.shape_type == self.RECT_SHAPE:
            lindex = (index + 1) % 4
            rindex = (index + 3) % 4
            lshift = None
            rshift = None
            if index % 2 == 0:
                lshift = QPointF(shiftPos.x(), 0)
                rshift = QPointF(0, shiftPos.y())
            else:
                rshift = QPointF(shiftPos.x(), 0)
                lshift = QPointF(0, shiftPos.y())
            shape.moveVertexBy(rindex, rshift)
            shape.moveVertexBy(lindex, lshift)
    def boundedMoveShape(self, shape, pos):
        if self.outOfPixmap(pos):
            return False  # No need to move
        o1 = pos + self.offsets[0]
        if self.outOfPixmap(o1):
            pos -= QPointF(min(0, o1.x()), min(0, o1.y()))
        o2 = pos + self.offsets[1]
        if self.outOfPixmap(o2):
            pos += QPointF(min(0, self.bg_image.width() - o2.x()),
                           min(0, self.bg_image.height() - o2.y()))
        # The next line tracks the new position of the cursor
        # relative to the shape, but also results in making it
        # a bit "shaky" when nearing the border and allows it to
        # go outside of the shape's area for some reason. XXX
        #self.calculateOffsets(self.selectedShape, pos)
        dp = pos - self.prevPoint
        if dp:
            shape.moveBy(dp)
            self.prevPoint = pos
            return True
        return False
    def deSelectShape(self):
        if self.selectedShape:
            self.selectedShape.selected = False
            self.selectedShape = None
            self.setHiding(False)
            self.selectionChanged.emit(False)
            self.update()
    def deleteSelected(self):
        if self.selectedShape:
            shape = self.selectedShape
            self.shapes.remove(self.selectedShape)
            self.selectedShape = None
            self.update()
            return shape
    def copySelectedShape(self):
        if self.selectedShape:
            shape = self.selectedShape.copy()
            self.deSelectShape()
            self.shapes.append(shape)
            shape.selected = True
            self.selectedShape = shape
            self.boundedShiftShape(shape)
            return shape
    def boundedShiftShape(self, shape):
        # Try to move in one direction, and if it fails in another.
        # Give up if both fail.
        point = shape[0]
        offset = QPointF(2.0, 2.0)
        self.calculateOffsets(shape, point)
        self.prevPoint = point
        if not self.boundedMoveShape(shape, point - offset):
            self.boundedMoveShape(shape, point + offset)
    def paintEvent(self, event):#所有的绘制操作都在paintEvent中完成
        if not self.bg_image:
            return super(Canvas, self).paintEvent(event)

        p = self._painter
        p.begin(self)#都在begin（）和end（）间完成
        p.setFont(QFont('Times', self.font_size, QFont.Bold))
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.scale(self.scale, self.scale)
        p.translate(self.offsetToCenter())

        p.drawImage(0, 0, self.bg_image)
        if self.task_mode == 3:
            p.setOpacity(0.3)
            p.drawImage(0,0,self.mask_pixmap)
            if self.brush_point:
                p.drawEllipse(self.brush_point,self.brush_size/2,self.brush_size/2)#椭圆
            if self.current_brush_path:
                if self.mask_pixmap.isNull():
                    self.mask_pixmap = QImage(self.bg_image.size(), QImage.Format_ARGB32)
                    self.mask_pixmap.fill(QColor(255,255,255,0))
                self.brush.begin(self.mask_pixmap)
                brush_pen = QPen()
                self.brush.setCompositionMode(QPainter.CompositionMode_Source)
                brush_pen.setColor(self.brush_color)
                brush_pen.setWidth(self.brush_size)
                brush_pen.setCapStyle(Qt.RoundCap)
                brush_pen.setJoinStyle(Qt.RoundJoin)
                self.brush.setPen(brush_pen)
                self.brush.drawPath(self.current_brush_path)
                self.brush.end()
        if self.task_mode==4:
            self.point_save=self.point_point_list
            w, h = self.bg_image.width(), self.bg_image.height()
            size = 4*min(w // 200, h // 200)
            if self.point_delete:
                print('delete point')
                self.point_point_list[self.point_delete-1]=None
                self.point_delete=False
            if self.point_rects:
                if self.point_rects_index==len(self.point_rects):
                    self.point_rects_index=0
                x,y,w,h=self.point_rects[self.point_rects_index]
                p.setPen(QColor(255, 0, 0))
                p.drawRect(x,y,w,h)

            if len(self.point_point_list)>0 :
                for i,point in enumerate(self.point_point_list):
                    if point and self.point_visible[i]:
                        p.setBrush(self.point_color[i])
                        p.setPen(self.point_color[i])
                        p.drawEllipse(float(point.x()-size//2), float(point.y() -size//2), size, size)
                        if i in self.point_cover:
                            if self.point_cover[i]==1:
                                p.setPen(QColor(255,0,0))
                                p.setFont(QFont('SimSun', size))
                                p.drawText(QRect(point.x(),point.y(), size, size), Qt.AlignLeft | Qt.AlignVCenter, '1')

            if self.point_dex :#注意这里剔除了0 0是none  高亮标注的操作  包括move
                p.setPen(QColor(255, 0, 0))
                p.setBrush(QColor(0, 0, 0, 0))
                try:
                    if self.point_point_list[self.point_dex - 1]:
                        p.drawRect(float(self.point_point_list[self.point_dex - 1].x() - size//2),
                                   float(self.point_point_list[self.point_dex - 1].y() - size//2), size, size)
                    if self.point_move:#移动
                        p.setPen(QColor(255, 0, 0))
                        p.drawLine(self.point_point_list[self.point_dex - 1], self.point_point)
                    if len(self.point_point_list) > 1:#画线
                        for i in self.point_link:  # 每次都要遍历所有的Link
                            if i[0] - 1 in range(len(self.point_point_list)) and i[1] - 1 in range(
                                    len(self.point_point_list)):
                                pen = QPen(Qt.red, 2)
                                p.setPen(pen)
                                if i not in self.point_link_save:
                                    self.point_link_save.append(i)
                                if self.point_point_list[i[0] - 1] and self.point_point_list[i[1] - 1]:
                                    p.drawLine(self.point_point_list[i[0] - 1], self.point_point_list[i[1] - 1])
                except IndexError:
                    pass
        if self.task_mode == 5 :#这里融合了point模型
            # 这个是用来画instances的框
            if self.parse_rects:
                p.setPen(QColor(255, 0, 0))

                x, y, w, h = self.parse_rects[self.parse_rects_index]
                p.setPen(QColor(255, 0, 0))
                p.drawRect(x, y, w, h)
        if self.task_mode==0 or self.task_mode==5:
            #这个部分用来添加框的虚线
            w, h = self.bg_image.width(), self.bg_image.height()
            size=min(w//200,h//200)
            pen=QPen(Qt.green,size,Qt.SolidLine)
            pen.setStyle(Qt.DashDotLine)
            p.setPen(pen)
            if self.xuxian:
                p.drawLine(self.xuxian.x(),self.xuxian.y(),self.xuxian.x(),self.xuxian.y()+h-20)
                p.drawLine(self.xuxian.x(), self.xuxian.y(), self.xuxian.x()+w-10, self.xuxian.y() )
        Shape.scale = self.scale
        for shape in self.shapes:
            if shape.fill_color:
                shape.fill = True
                shape.paint(p)###这里是其他模式的调用shape中的Paint函数
            elif (shape.selected or not self._hideBackround) and self.isVisible(shape):
                shape.fill = shape.selected or shape == self.hShape
                shape.paint(p)
        if self.current:
            self.current.paint(p)
            self.line.paint(p)
        if self.selectedShapeCopy:
            self.selectedShapeCopy.paint(p)
        # Paint rect
        if self.current is not None and len(self.line) == 2:
            leftTop = self.line[0]
            rightBottom = self.line[1]
            rectWidth = rightBottom.x() - leftTop.x()
            rectHeight = rightBottom.y() - leftTop.y()
            color = QColor(0, 220, 0)
            p.setPen(color)
            brush = QBrush(Qt.BDiagPattern)
            p.setBrush(brush)
            if self.shape_type == self.RECT_SHAPE:
                p.drawRect(leftTop.x(), leftTop.y(), rectWidth, rectHeight)
        p.end()#
    # parse mode
    def parse_next_rect(self):
        print("canvas_parse_shapes",self.parse_shapes)
        #这个函数的主要作用是下一个框的保存值
        #先保存每个object的相应任务的值
        if self.parse_rects_index!=0:
        #这里的parse_rects_index都是表示的是下一个框的index
            self.parse_shapes[self.parse_rects_index-1]=self.shapes
        else:
            self.parse_shapes[self.parse_rects_num-1] = self.shapes
        #再看看能不能赋值，不能赋值就直接给空值就可以
        if self.parse_rects_index in self.parse_shapes:
            self.shapes=self.parse_shapes[self.parse_rects_index]
        else:
            self.shapes=[]
        #最后重新绘制即可，这里是一定要加上的，这里加了上面的就不用加了。
        self.repaint()
    def parse_new_bbox(self):
        #这个函数主要是对新的操作所产生的shape做存值的处理
        #注意新的操作至少要写分为三个操作：1、新增2、删除3、移动等
        if self.parse_rects_index!=0:
        # 这里的parse_rects_index都是表示的是下个框的index
            self.parse_shapes[self.parse_rects_index]=self.shapes
        elif len(self.parse_shapes)>0 and not self.parse_rects_index==0:
            self.parse_shapes[self.parse_rects_num-1] = self.shapes
        # 0的特殊性
        else:
            self.parse_shapes[0] = self.shapes
    def parse_clear(self):
        #这个函数的所有的定义的初始化变量都要重新初始化
        #在主函数里写在nextimg preimg
        self.parse_shapes = {}
        self.shapes = []
        self.repaint()
        self.parse_rects_index=0
    # point mode
    def deletepoint(self,i):
        self.point_delete=i
    def point_finish(self):
        del self.point_point_list[-1]
        self.point_dex = self.point_num-1
        QMessageBox.about(self, "About", self.tr(
            '<p><b>%s</b></p>%s <p>%s</p>' % ('注意标注已经为', str(self.point_num + 1) + '个', '只可修改')))
        self.repaint()
    def point_change(self,id,visible):
        # self.point_changed=True
        if id:
            if visible:
                self.point_visible[id]=True
                if id<=len(self.point_point_list):#当前的点在point list 并且可视化
                    self.point_dex=id
                    self.repaint()
                else:#当前的点不在point list 但是想可视
                    self.point_dex = self.point_dex
                    # self.Point_Error.emit(True,id)
            else:#不可见  那个这个点的值就是None
                if id <=len(self.point_point_list):#当前的点在point list 并且不可视
                    pass#
                    # print('v1')
                    # self.point_point_list[id] =self.point_point
                    # self.point_visible[id]=True
                    # self.repaint()
                else:
                    try:
                        self.point_point_list[id]=None
                        self.point_visible[id] = False
                        self.repaint()
                        print('pointlink delete')
                    except IndexError:
                        pass
        else :#针对 全选
            pass
    def point_modify(self,i):
        if i in range(len(self.point_point_list)):
            print('modified',i)
            self.point_modified=i+1
    def point_all_delete(self):
        self.point_changed=True
        self.point_all_deleted=True
        l=[i for i in range(len(self.point_point_list))]
        # self.point_cover = {i: 2 for i in range(len(self.point_link)-2)}
        self.point_point_list=[]
        self.point_dex=0
        self.Point_Change.emit(0,True,l)#调到第一个参数
        # self.point_shape[self.point_rects_index]=[]
        self.repaint()
    def point_load_point_shape(self,point_list):
        point = []
        print('canvas point_shape',point_list)
        for i,ll in enumerate(point_list):
            print("ll")
            if not ll:
                print("list",ll)
                self.point_shape[i] = []
                self.point_dex = 1
                self.repaint()
            else:
                for p in ll:
                    point.append(QPointF(int(p[0]), int(p[1])))
                self.point_shape[i] = point
                point = []
            if len(self.point_shape[0])>0:
                self.point_point_list= self.point_shape[self.point_rects_index]

            self.point_dex = len(self.point_point_list)
            self.repaint()
    def point_load(self,point_list):#transform list to qpointf list
        point=[]
        rect_dex=0
        if not point_list:
            self.point_point_list=[]
            self.point_dex = 1
            self.repaint()
        else:
            for p in point_list:
                point.append(QPointF(int(p[0]),int(p[1])))
            self.point_point_list=point
            self.point_shape[self.point_rects_index]=self.point_point_list
            self.point_dex=len(self.point_point_list)
            self.repaint()
    def point_rect_points(self,x,y,w,h):
        self.point_rects.append([x,y,w,h])
    # next rect
    def draw_rects(self,rects):
        #主要对xml分析后进来的rects处理
        self.parse_rects=rects
        self.parse_rects_num=len(self.parse_rects)
        self.repaint()
    def draw_point_single_img(self,point_point_list,i):
        self.point_shape[i] = self.point_point_list
    def draw_next_rect(self):
        point_point_list=[]
        if self.point_changed:
            if len(self.point_shape)<=len(self.point_rects):
                self.point_shape[self.point_rects_index]=self.point_point_list
        self.point_rects_index += 1
        if self.point_rects_index == len(self.point_rects):
            self.point_rects_index =0
        self.point_point_list = []  # .clear 清内存 最好不要这样
        self.point_dex = 0
        if self.point_rects_index in self.point_shape:
            point_point_list = self.point_shape[self.point_rects_index]
        else:
            pass
        if point_point_list and isinstance(point_point_list[0],QPointF):#绘制过程
            self.point_point_list=point_point_list
            self.point_dex=len(self.point_point_list)
            self.repaint()
        else:#加载过程
            print("point_point_list",point_point_list)
            self.point_load(point_point_list)
    ##############
    def transformPos(self, point):
        """Convert from widget-logical coordinates to painter-logical coordinates."""
        return point / self.scale - self.offsetToCenter()
    def offsetToCenter(self):
        s = self.scale
        area = super(Canvas, self).size()
        if self.bg_image:
            w, h = self.bg_image.width() * s, self.bg_image.height() * s
        else:
            w,h = 100,100
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QPointF(x, y)
    def outOfPixmap(self, p):
        if self.bg_image:
            w, h = self.bg_image.width(), self.bg_image.height()
            return not (0 <= p.x() <= w and 0 <= p.y() <= h)
    def finalise(self):#完成
        assert self.current
        self.current.close()
        self.shapes.append(self.current)
        self.current = None
        self.setHiding(False)
        self.newShape.emit()
        self.update()
        self.xuxian=None
        self.start=False
        self.started=False
    def closeEnough(self, p1, p2):
        #d = distance(p1 - p2)
        #m = (p1-p2).manhattanLength()
        # print "d %.2f, m %d, %.2f" % (d, m, d - m)
        return distance(p1 - p2) < self.epsilon
    def intersectionPoint(self, p1, p2):
        # Cycle through each image edge in clockwise fashion,
        # and find the one intersecting the current line segment.
        # http://paulbourke.net/geometry/lineline2d/
        size = self.bg_image.size()
        points = [(0, 0),
                  (size.width(), 0),
                  (size.width(), size.height()),
                  (0, size.height())]
        x1, y1 = p1.x(), p1.y()
        x2, y2 = p2.x(), p2.y()
        try:
            d, i, (x, y) = min(self.intersectingEdges((x1, y1), (x2, y2), points))
        except:
            pass
        x3, y3 = points[i]
        x4, y4 = points[(i + 1) % 4]
        if (x, y) == (x1, y1):
            # Handle cases where previous point is on one of the edges.
            if x3 == x4:
                return QPointF(x3, min(max(0, y2), max(y3, y4)))
            else:  # y3 == y4
                return QPointF(min(max(0, x2), max(x3, x4)), y3)
        return QPointF(x, y)
    def intersectingEdges(self, xxx_todo_changeme, xxx_todo_changeme1, points):
        """For each edge formed by `points', yield the intersection
        with the line segment `(x1,y1) - (x2,y2)`, if it exists.
        Also return the distance of `(x2,y2)' to the middle of the
        edge along with its index, so that the one closest can be chosen."""
        (x1, y1) = xxx_todo_changeme
        (x2, y2) = xxx_todo_changeme1
        for i in range(4):
            x3, y3 = points[i]
            x4, y4 = points[(i + 1) % 4]
            denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
            nua = (x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)
            nub = (x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)
            if denom == 0:
                # This covers two cases:
                #   nua == nub == 0: Coincident
                #   otherwise: Parallel
                continue
            ua, ub = nua / denom, nub / denom
            if 0 <= ua <= 1 and 0 <= ub <= 1:
                x = x1 + ua * (x2 - x1)
                y = y1 + ua * (y2 - y1)
                m = QPointF((x3 + x4) / 2, (y3 + y4) / 2)
                d = distance(m - QPointF(x2, y2))
                yield d, i, (x, y)
    # These two, along with a call to adjustSize are required for the
    # scroll area.
    def sizeHint(self):
        return self.minimumSizeHint()
    def minimumSizeHint(self):
        if self.bg_image:
            return self.scale * self.bg_image.size()
        return super(Canvas, self).minimumSizeHint()
    def wheelEvent(self, ev):
        mods = ev.modifiers()
        if Qt.ControlModifier == int(mods):  # ctrl键
            self.zoomRequest.emit(ev.angleDelta().y())
        else:
            ev.angleDelta().y() and self.scrollRequest.emit(
                ev.angleDelta().y(), Qt.Horizontal if (
                        Qt.ShiftModifier == int(mods)) else Qt.Vertical)
            ev.angleDelta().x() and self.scrollRequest.emit(ev.angleDelta().x(), Qt.Horizontal)
        ev.accept()
    def keyPressEvent(self, ev):#键盘事件
        key = ev.key()
        if self.task_mode==4:
            if key==Qt.Key_0:
                self.point_point_list.append(None)
                self.point_visible[self.point_dex]=False
                self.Point_Change.emit(self.point_dex+1,False,[])#当前点的下一个点，自动移动到当前点的下一个点   第一个参数为选择的item的id，第二个参数为非选择状态，第三个参数为全删除的当前的list
                self.point_dex += 1#point_dex 从1开始表示当前点的dex (包括指向点和下一个即将绘制的点)
            elif key==Qt.Key_1:#在这里对全局变量进行键盘判断，不需要self.repaint()
                self.point_cover[self.point_dex-1]=1
                self.point_cover_change=True
            elif key==Qt.Key_2:
                if self.point_cover[self.point_dex-1]==1:
                    self.point_cover[self.point_dex-1]=2
                self.point_cover_change=True


        if key == Qt.Key_Escape and self.current:
            print ('ESC press')
            self.current = None
            #虚线的初始化
            self.xuxian = None
            self.start = False
            self.started = False
            ###########
            self.drawingPolygon.emit(False)
            self.update()
        elif key == Qt.Key_Return and self.canCloseShape():
            self.finalise()
    def setLastLabel(self, text):
        assert text
        self.shapes[-1].label = text
        return self.shapes[-1]
    def setSelectedShape(self, ignore):
        """
        :param ignore:
        :return: you can set everything from the label main function
        """
        if self.selectedShape:
            self.selectedShape.ignore = ignore
            self.repaint()
    def undoLastLine(self):
        assert self.shapes
        self.current = self.shapes.pop()
        self.current.setOpen()
        self.line.points = [self.current[-1], self.current[0]]
        self.drawingPolygon.emit(True)
    def resetAllLines(self):
        assert self.shapes
        self.current = self.shapes.pop()
        self.current.setOpen()
        self.line.points = [self.current[-1], self.current[0]]
        self.drawingPolygon.emit(True)
        self.current = None
        self.drawingPolygon.emit(False)
        self.update()
    def loadMaskmap(self,mask):
        self.mask_pixmap = mask
        self.repaint()
    def loadPixmap(self, pixmap):
        self.bg_image = pixmap
        self.shapes = []
        self.mask_pixmap = QImage(self.bg_image.size(), QImage.Format_ARGB32)
        self.mask_pixmap.fill(QColor(255,255,255,0))
        self.repaint()
    def loadShapes(self, shapes):
        self.shapes = list(shapes)

        self.shape_type = shapes[0].get_shape_type()
        self.current = None
        self.repaint()

    def setShapeVisible(self, shape, value):
        self.visible[shape] = value
        self.repaint()

    def overrideCursor(self, cursor):
        self.restoreCursor()
        self._cursor = cursor
        QApplication.setOverrideCursor(cursor)

    def restoreCursor(self):
        QApplication.restoreOverrideCursor()
    def resetState(self):
        self.restoreCursor()
        # self.bg_image = None
        self.update()
    def update_image(self,img):
        self.bg_image=img
        self.repaint()

