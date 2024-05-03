import view
import model
import os
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
from PyQt5 import QtCore
from PyQt5.QtWidgets import *

class MY_Controller:

    def __init__(self):
        # 加载ui界面类，用于设置ui
        self.view = view.MY_View()
        # 加载数据处理类
        self.model = model.MY_Model()
        # 标记raw数据是否已经读入
        self.flag1 = 0
        # 标记是否已经完成参考转换
        self.flag2 = 0
        # 标记批处理模式是否读入数据
        self.flag3 = 0
        # 信号与槽设置
        self.view.dataload_button.clicked.connect(self.dataload_slot)
        self.view.info_button.clicked.connect(self.info_slot)
        self.view.Preprocess_button.clicked.connect(self.Preprocess_slot)
        self.view.process_button.clicked.connect(self.process_slot)
        self.view.quick_save.clicked.connect(self.quick_save_slot)
        self.view.save.clicked.connect(self.save_slot)
        self.view.details_botton1.clicked.connect(self.details_slot1)
        self.view.details_botton2.clicked.connect(self.details_slot2)
        self.view.pushButton.clicked.connect(self.dataload2_slot)
        self.view.pushButton_3.clicked.connect(self.process2_slot)

        # 存放批处理数据的路径
        self.filepath2 = list()

        self.view.show()

    def dataload_slot(self):
        #选择读取路径
        file_dialog = QFileDialog(self.view)
        file_dialog.setNameFilter("*.set *.fif *.edf")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            print("加载文件:", file_path)
            self.model.dataload(file_path)
            self.model.raw.plot()
            self.showgraph_raw()
            # flag设置为1
            self.flag1 = 1
        # 如果数据还未转换，清空画布，排除上次读取的影响
        if self.flag2 == 1:
            scene = QGraphicsScene()
            self.view.graph2.setScene(scene)
            self.view.graph2.show()
            self.flag2 = 0

    # graphicview上显示raw图像
    def showgraph_raw(self):
        scene = QGraphicsScene()
        # 在MNE中绘制原始数据并保存为图片
        fig = self.model.raw.plot(show=False)
        fig.savefig('picture/raw_data_plot.png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        # 加载保存的图片
        pixmap = QPixmap('picture/raw_data_plot.png')
        # 创建GraphicsPixmapItem并添加到Graphics Scene中
        pixmap_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(pixmap_item)
        self.view.graph1.setScene(scene)
        self.view.graph1.show()

    # graphicview上显示raw_after图像
    def showgraph_raw_after(self):
        scene = QGraphicsScene()
        # 在MNE中绘制原始数据并保存为图片
        fig = self.model.raw_after.plot(show=False)
        fig.savefig('picture/raw_after_data_plot.png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        # 加载保存的图片
        pixmap = QPixmap('picture/raw_after_data_plot.png')
        # 创建GraphicsPixmapItem并添加到Graphics Scene中
        pixmap_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(pixmap_item)
        self.view.graph2.setScene(scene)
        self.view.graph2.show()

    def info_slot(self):
        # 判断数据是否已经读入
        if self.flag1 == 1:
            print("正在查看数据详情...")
            # 创建info选择视图
            self.view.setupUi_selectinfo()
            self.view.selectinfo1.clicked.connect(self.info1)
            self.view.selectinfo2.clicked.connect(self.info2)
            self.view.selectinfo3.clicked.connect(self.info3)
            self.view.selectinfo.show()
        # 数据未读入则弹出警示框
        else:
            QMessageBox.warning(self.view, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    # 显示参数详情
    def info1(self):
        # 隐藏上一级窗口
        self.view.selectinfo.hide()
        QMessageBox.information(self.view, '脑电数据信息', str(self.model.raw.info))

    # 显示蒙太奇
    def info2(self):
        self.view.selectinfo.hide()
        try:
            montage = self.model.raw.get_montage()
            montage.plot()
        except:
            QMessageBox.warning(self.view, '警告', '该脑电数据不支持蒙太奇显示', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    # 显示功率谱密度图
    def info3(self):
        self.view.selectinfo.hide()
        try:
            self.model.raw.plot_psd()
        except:
            QMessageBox.warning(self.view, '警告', '该脑电数据不支持功率谱密度图显示', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def Preprocess_slot(self):
        if self.flag1 == 1:
            print("正在进行数据预处理...")
            self.view.setupUi_selectPreprocess()
            self.view.selectPreprocess1.clicked.connect(self.Preprocess1)
            self.view.selectPreprocess2.clicked.connect(self.Preprocess2)
            self.view.selectPreprocess3.clicked.connect(self.Preprocess3)
            self.view.selectPreprocess.show()
        else:
            QMessageBox.warning(self.view, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    # 脑电数据裁剪
    def Preprocess1(self):
        self.view.selectPreprocess.hide()
        self.view.setupUi_selectPreprocess1()
        self.view.preprocess1.show()
        self.view.preprocess1.confirm_button.clicked.connect(self.cropslot)

    def cropslot(self):
        t1 = float(self.view.preprocess1.start_edit.text())
        t2 = float(self.view.preprocess1.end_edit.text())
        self.view.preprocess1.hide()
        try:
            self.model.crop(t1, t2)
        except ValueError:
            # 如果出现ValueError，报错并要求重新输入
            QMessageBox.warning(self.view, '警告', '数值超出范围，请重新输入', QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes)
            self.Preprocess1()
        else:
            self.showgraph_raw()
            QMessageBox.information(self.view, '数据裁剪', '数据已裁剪')

    # 脑电数据滤波
    def Preprocess2(self):
        self.view.selectPreprocess.hide()
        self.view.setupUi_selectPreprocess2()
        self.view.preprocess2.show()
        self.view.preprocess2.confirm_button.clicked.connect(self.filterslot)

    def filterslot(self):
        f1 = float(self.view.preprocess2.start_edit.text())
        f2 = float(self.view.preprocess2.end_edit.text())
        self.view.preprocess2.hide()
        if f1 >= self.model.raw.info['highpass'] and f2 <= self.model.raw.info['lowpass']:
            self.model.filter(f1, f2)
            self.showgraph_raw()
            QMessageBox.information(self.view, '数据滤波', '数据已滤波')
        else:
            QMessageBox.warning(self.view, '警告', '数值超出范围，请重新输入', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            self.Preprocess2()

    # 脑电数据重采样
    def Preprocess3(self):
        self.view.selectPreprocess.hide()
        self.view.setupUi_selectPreprocess3(self.model.raw)
        self.view.preprocess3.show()
        self.view.preprocess3.confirm_button.clicked.connect(self.resample_slot)

    def resample_slot(self):
        f = float(self.view.preprocess3.resample_edit.text())
        self.view.preprocess3.hide()
        if f <= self.model.raw.info['sfreq'] and f >= 0:
            self.model.raw.resample(sfreq=f)
            self.showgraph_raw()
            QMessageBox.information(self.view, '数据重采样', '重采样成功')
        else:
            QMessageBox.warning(self.view, '警告', '数值不合理，请重新输入', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            self.Preprocess3()

    def process_slot(self):
        if self.flag1 == 1:
            self.view.setupUi_selectprocess()
            self.view.selectprocess0.clicked.connect(self.set_reference)
            self.view.selectprocess1.clicked.connect(self.set_LM)
            self.view.selectprocess2.clicked.connect(self.set_AR)
            self.view.selectprocess3.clicked.connect(self.set_REST)
            self.view.selectprocess.show()
        else:
            QMessageBox.warning(self.view, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def set_reference(self):
        self.view.selectprocess.hide()
        self.view.setupUi_set_reference(self.model.raw)
        self.view.selectreference.show()
        self.view.selectreference.pb.clicked.connect(self.setslot)

    def setslot(self):
        print("正在转换参考...")
        self.view.selectreference.hide()
        channel = self.view.selectreference.cb.currentText()
        channel_chosed = list()
        channel_chosed.append(channel)
        self.model.set_reference(channel_chosed)
        self.model.raw_after.plot()
        _translate = QtCore.QCoreApplication.translate
        #显示当前采用的转换方式
        self.view.text1.setText("转换方式：单个电极(" + channel + ")")
        self.view.text1.setStyleSheet('color: orangered')
        self.showgraph_raw_after()
        self.flag2 = 1
        # 标记当前参考方式
        self.model.setreference(0)

    def set_LM(self):
        print("正在转换参考...")
        self.view.selectprocess.hide()
        print("正在转换为双侧乳突平均参考...")
        try:
            self.model.set_LM()
        except:
            # 如果出现错误，报错并要求更换参考方式
            print("LM参考转换失败...")
            QMessageBox.warning(self.view, '警告', '脑电记录电极中不包含左右乳突，请选取其他参考方式', QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes)
            self.process_slot()
        else:
            self.model.raw_after.plot()
            _translate = QtCore.QCoreApplication.translate
            # 显示当前采用的转换方式
            self.view.text1.setText("转换方式：LM")
            self.view.text1.setStyleSheet('color: orangered')
            self.flag2 = 1
            self.model.setreference(1)
            self.showgraph_raw_after()

    def set_AR(self):
        print("正在转换参考...")
        self.view.selectprocess.hide()
        print("正在转换为平均参考...")
        self.model.set_AR()
        self.model.raw_after.plot()
        _translate = QtCore.QCoreApplication.translate
        self.view.text1.setText("转换方式:AR")
        self.view.text1.setStyleSheet('color: orangered')
        self.flag2 = 1
        self.model.setreference(2)
        self.showgraph_raw_after()

    def set_REST(self):
        print("正在转换参考...")
        self.view.selectprocess.hide()
        print("正在转换为REST参考...")
        try:
            self.model.set_REST()
        except:
            # 如果出现错误，报错并要求更换参考方式
            print("REST参考转换失败...")
            QMessageBox.warning(self.view, '警告', '该脑电记录不支持REST参考，请选择其他参考方式',
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes)
            self.process_slot()
        else:
            self.model.raw_after.plot()
            _translate = QtCore.QCoreApplication.translate
            # 显示当前采用的转换方式
            self.view.text1.setText("转换方式：REST")
            self.view.text1.setStyleSheet('color: orangered')
            self.flag2 = 1
            self.model.setreference(3)
            self.showgraph_raw_after()

    def quick_save_slot(self):
        if self.flag1 == 1 and self.flag2 == 1:
            # 进行过参考转换，则保存参考转换后的数据
            if self.model.reference == 0:
                after_path = self.model.file_path[0:-4] + '_SET_raw.fif'
                self.model.save(after_path)
            if self.model.reference == 1:
                after_path = self.model.file_path[0:-4] + '_LM_raw.fif'
                self.model.save(after_path)
            elif self.model.reference == 2:
                after_path = self.model.file_path[0:-4] + '_AR_raw.fif'
                self.model.save(after_path)
            elif self.model.reference == 3:
                after_path = self.model.file_path[0:-4] + '_REST_raw.fif'
                self.model.save(after_path)
            QMessageBox.information(self.view, '保存', '一键保存成功')
        elif self.flag1 == 1 and self.flag2 == 0:
            # 如果没有进行参考转换，则保存参考转换前的数据
            self.model.save(self.model.file_path[0:-4] + '_raw.fif')
        else:
            QMessageBox.warning(self.view, '警告', '请先转换数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def save_slot(self):
        if self.flag1 == 1 and self.flag2 == 1:
            file_dialog2 = QFileDialog()
            if self.model.reference == 0:
                save_path, ok = file_dialog2.getSaveFileName(self.view, '选择保存路径',
                                                             self.model.file_path[0:-4] + '_SET_raw.fif',
                                                             'fif(*.fif)')
                if ok:
                    self.model.save(save_path)
                    QMessageBox.information(self.view, '保存', '保存成功')
            elif self.model.reference == 1:
                save_path, ok = file_dialog2.getSaveFileName(self.view, '选择保存路径',
                                                             self.model.file_path[0:-4] + '_LM_raw.fif',
                                                             'fif(*.fif)')
                if ok:
                    self.model.save(save_path)
                    QMessageBox.information(self.view, '保存', '保存成功')
            elif self.model.reference == 2:
                save_path, ok = file_dialog2.getSaveFileName(self.view, '选择保存路径',
                                                             self.model.file_path[0:-4] + '_AR_raw.fif',
                                                             'fif(*.fif)')
                if ok:
                    self.model.save(save_path)
                    QMessageBox.information(self.view, '保存', '保存成功')
            elif self.model.reference == 3:
                save_path, ok = file_dialog2.getSaveFileName(self.view, '选择保存路径',
                                                             self.model.file_path[0:-4] + '_REST_raw.fif',
                                                             'fif(*.fif)')
                if ok:
                    self.model.save(save_path)
                    QMessageBox.information(self.view, '保存', '保存成功')
        elif self.flag1 == 1 and self.flag2 == 0:
            # 如果没有进行参考转换，则保存参考转换前的数据
            file_dialog2 = QFileDialog()
            save_path, ok = file_dialog2.getSaveFileName(self.view, '选择保存路径',
                                                         self.model.file_path[0:-4] + '_raw.fif',
                                                         'fif(*.fif)')
            if ok:
                self.model.save(save_path)
                QMessageBox.information(self.view, '保存', '保存成功')
        else:
            QMessageBox.warning(self.view, '警告', '请先转换数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def details_slot1(self):
        if self.flag1 == 1:
            self.model.raw.plot()
            self.showgraph_raw()
        else:
            QMessageBox.warning(self.view, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def details_slot2(self):
        if self.flag1 == 1:
            if self.flag2 == 1:
                self.model.raw_after.plot()
                self.showgraph_raw_after()
            else:
                QMessageBox.warning(self.view, '警告', '请先进行参考转换', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            QMessageBox.warning(self.view, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def dataload2_slot(self):
        # 数据路径列表清空
        self.filepath2.clear()
        self.dir_path = QFileDialog.getExistingDirectory(self.view, '选择待处理数据的文件夹', os.getcwd())
        if self.dir_path != '':
            files = os.listdir(self.dir_path)  # 得到文件夹路径
            self.num = 0
            for file in files:  # 按照顺序在 files 里面进行每一个文件的 数据名称 循环读取
                # 如果用户选中*.fif的checkBox，读入*.fif文件
                if self.view.checkBox.isChecked():
                    if file[-4:] == '.fif':
                        self.filepath2.append(file)
                        self.num += 1
                # 如果用户选中*.set的checkBox，读入*.set文件
                if self.view.checkBox_2.isChecked():
                    if file[-4:] == '.set':
                        self.filepath2.append(file)
                        self.num += 1
                # 如果用户选中*.edf的checkBox，读入*.edf文件
                if self.view.checkBox_3.isChecked():
                    if file[-4:] == '.edf':
                        self.filepath2.append(file)
                        self.num += 1
            QMessageBox.information(self.view, '数据读取', '批处理数据读取成功')
            # 标记数据已读取
            self.flag3 = 1


    def process2_slot(self):
        if self.flag3 == 1:
            if self.num != 0:
                self.view.progressBar.setRange(0, self.num)
            # 如果没有勾选参考方式，弹出警示框
            if not self.view.radioButton.isChecked() and not self.view.radioButton_2.isChecked():
                QMessageBox.warning(self.view, '警告', '请先选择转换方式', QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.Yes)
            else:
                self.save_path = QFileDialog.getExistingDirectory(self.view, '选择待保存数据的文件夹', os.getcwd())
                if self.save_path != '':
                    # 如果选中AR为参考转换方式
                    if self.view.radioButton.isChecked():
                        for file in self.filepath2:
                            # 读取的路径
                            filepath1 = self.dir_path + '/' + file
                            # 保存的路径
                            filepath2 = self.save_path + '/' + file
                            # 读取数据参考转换并保存
                            self.model.dataload(filepath1)
                            self.model.set_AR()
                            self.model.save(filepath2[0:-4] + '_AR_raw.fif')
                            self.view.progressBar.pv += 1
                            self.view.progressBar.setValue(self.view.progressBar.pv)
                        QMessageBox.information(self.view, '参考转换', 'AR参考转换批处理保存成功')
                    # 如果选中REST为参考转换方式
                    elif self.view.radioButton_2.isChecked():
                        #标记是否有脑电数据不支持REST转换
                        flag = 0
                        for file in self.filepath2:
                            filepath1 = self.dir_path + '/' + file
                            filepath2 = self.save_path + '/' + file
                            self.model.dataload(filepath1)
                            # 防止部分数据不支持REST参考转换
                            try:
                                self.model.set_REST()
                            except:
                                self.view.progressBar.pv += 1
                                self.view.progressBar.setValue(self.view.progressBar.pv)
                                flag = 1
                            else:
                                self.model.save(filepath2[0:-4] + '_REST_raw.fif')
                                self.view.progressBar.pv += 1
                                self.view.progressBar.setValue(self.view.progressBar.pv)
                        if flag == 0:
                            QMessageBox.information(self.view, '参考转换', 'REST参考转换批处理保存成功')
                        else:
                            QMessageBox.warning(self.view, '警告', '部分数据不支持REST参考转换，已经自动跳过', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    self.view.progressBar.reset()
                    self.view.progressBar.pv = 0
                    self.flag3 = 0
        else:
            QMessageBox.warning(self.view, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)