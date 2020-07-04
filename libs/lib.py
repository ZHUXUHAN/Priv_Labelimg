from math import sqrt

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


def newIcon(icon):
    img = QImage(':/' + icon)
    pixmap = QPixmap(img)#注意可以在这里自适应的图标对应的图片的大小
    fitPixmap = pixmap.scaled(40,40, Qt.IgnoreAspectRatio,
                              Qt.SmoothTransformation)  # 注意 scaled() 返回一个 QtGui.QPixmap
    icon = QIcon(fitPixmap)
    return icon
    # return QIcon(':/' + icon)#图标


def newButton(text, icon=None, slot=None):
    b = QPushButton(text)
    if icon is not None:
        b.setIcon(newIcon(icon))
    if slot is not None:
        b.clicked.connect(slot)
    return b


def newAction(parent, text, slot=None, shortcut=None, icon=None,#主要为qaction做一些快捷键，提示信息等的设置。
              tip=None, checkable=False, enabled=True):
    """Create a new action and assign callbacks, shortcuts, etc."""
    a = QAction(text, parent)#Qicon，
    if icon is not None:
        a.setIcon(newIcon(icon))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):#设置一种快捷方式
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)#设置菜单栏选项或者工具栏选项是否可以可以操作，如果为False则是不可以操作的
    return a


def addActions(widget, actions):#为菜单栏的添加action或者menu对象
    for action in actions:
        if action is None:
            widget.addSeparator()#添加分割符
        elif isinstance(action, QMenu):#如果是menu，则添加一个menu对象
            widget.addMenu(action)
        else:
            widget.addAction(action)


def labelValidator():#标注的lineedit的输入的验证器
    return QRegExpValidator(QRegExp(r'^[^ \t].+'), None)#限制文本输入的格式


class struct(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)#用来更新字典型的函数


def distance(p):
    return sqrt(p.x() * p.x() + p.y() * p.y())


def fmtShortcut(text):
    mod, key = text.split('+', 1)
    return '<b>%s</b>+<b>%s</b>' % (mod, key)
