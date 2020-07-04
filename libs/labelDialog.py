#标注框
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from libs.lib import newIcon, labelValidator

BB = QDialogButtonBox


class SubListWidget(QDialog):

    def __init__(self, parent=None, listItem=None):
        self.setWindowTitle('select a label')#左下角的列表框子
        self.select_text = None
        super(SubListWidget, self).__init__(parent)
        self.listwidget = QListWidget(self)
        layout = QVBoxLayout()
        if listItem is not None and len(listItem) > 0:
            for item in listItem:
                self.listwidget.addItem(item)
        layout.addWidget(self.listwidget)
        self.setLayout(layout)
        self.listwidget.itemDoubleClicked.connect(self.listItemDoubleClicked)
        self.move(QCursor.pos())

    def get_select_item(self):
        return self.select_text if self.exec_() else None

    def listItemDoubleClicked(self, tQListWidgetItem):
        text = tQListWidgetItem.text().trimmed()
        self.select_text = text
        if text is not None:
            self.accept()


class LabelDialog(QDialog):#标注的小框子

    def __init__(
            self,
            text="Enter object label",
            parent=None,
            listItem=None,
            sub_label_items=None,
            label_fre_dic=None):
        super(LabelDialog, self).__init__(parent)
        self.edit = QLineEdit()#小框子上面的小的文本框
        self.edit.setText(text)
        self.edit.setValidator(labelValidator())#整个文本限制器在libs.lib里
        self.edit.editingFinished.connect(self.postProcess)#输入完后显示出来
        layout = QVBoxLayout()
        self.label_fre_dic = label_fre_dic
        layout.addWidget(self.edit)
        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon('done'))
        bb.button(BB.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.validate)#确认按键
        bb.rejected.connect(self.reject)#取消按键 直接退出
        layout.addWidget(bb)
        if sub_label_items:
            self.sub_labels_dic = sub_label_items
            self.sublistwidget = SubListWidget()
            if self.sub_labels_dic.keys() is not None and len(self.sub_labels_dic.keys()) > 0:
                self.listWidget = QListWidget(self)
            keys = sorted(self.sub_labels_dic.keys())
            for item in keys:
                self.listWidget.addItem(item)
            self.listWidget.itemClicked.connect(self.listItemClicked)
            layout.addWidget(self.listWidget)

        elif listItem:
            sorted_labels = []
            if self.label_fre_dic:
                print (label_fre_dic)
                sorted_labels = sorted(
                    self.label_fre_dic,
                    key=self.label_fre_dic.get,
                    reverse=True)
            if listItem is not None and len(listItem) > 0:
                self.listWidget = QListWidget(self)
            for item in sorted_labels:
                self.listWidget.addItem(item)
            self.listWidget.itemDoubleClicked.connect(
                self.listItemDoubleClicked)
            layout.addWidget(self.listWidget)
        self.setLayout(layout)

    def validate(self):
        if self.edit.text().strip():#if self.edit.text().trimmed():

            self.accept()#确认按键,会直接退出的

    def postProcess(self):#为lineedit设置文字,在于掩码确认后输出，但是好像不起作用
        self.edit.setText(self.edit.text().strip())#self.edit.setText(self.edit.text().trimmed())

    def popUp(self, text='', move=True):
        self.edit.setText(text)
        self.edit.setSelection(0, len(text))
        self.edit.setFocus(Qt.PopupFocusReason)
        if move:
            self.move(QCursor.pos())
        return self.edit.text() if self.exec_() else None

    def listItemDoubleClicked(self, tQListWidgetItem):#
        text = tQListWidgetItem.text().strip()# text = tQListWidgetItem.text().trimmed()
        self.edit.setText(text)
        self.validate()#如果想双击完选项立即退出 加上这句话

    def sublistwidgetclicked(self, tQListWidgetItem):  # 暂时没用
        print(tQListWidgetItem.text().trimmed())

    def listItemClicked(self, tQListWidgetItem):#暂时没用
        self.sublistwidget.close()
        labels = self.sub_labels_dic[str(tQListWidgetItem.text().trimmed())]
        label_dic = {}
        for label in labels:
            if label in self.label_fre_dic:
                label_dic[label] = self.label_fre_dic[label]
            else:
                label_dic[label] = 0
        sorted_labels = sorted(label_dic, key=label_dic.get, reverse=True)
        self.sublistwidget = SubListWidget(listItem=sorted_labels, parent=self)
        self.sublistwidget.show()
        self.edit.setText(self.sublistwidget.get_select_item())
        self.validate()
