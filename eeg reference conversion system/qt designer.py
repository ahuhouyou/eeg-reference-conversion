import sys
import mne
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from MY_UI import Ui_MainWindow
import warnings

class MyWin(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWin, self).__init__(parent)
        # 标记raw数据是否已经读入
        self.flag = 0
        # 标记是否已经完成参考转换
        self.flag2 = 0
        self.setupUi(self)
        self.dataload_button.clicked.connect(self.dataload_slot)
        self.info_button.clicked.connect(self.info_slot)
        self.Preprocess_button.clicked.connect(self.Preprocess_slot)
        self.process_button.clicked.connect(self.process_slot)
        self.quick_save.clicked.connect(self.quick_save_slot)
        self.save.clicked.connect(self.save_slot)
        self.details_botton1.clicked.connect(self.details_slot1)
        self.details_botton2.clicked.connect(self.details_slot2)

    def dataload_slot(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("*.set")
        if file_dialog.exec_():
            self.file_path = file_dialog.selectedFiles()[0]
            print("加载文件:", self.file_path)
        self.raw = mne.io.read_raw_eeglab(self.file_path, preload = True)
        self.raw.plot()
        self.showgraph_raw()
        self.flag = 1

    def info_slot(self):
        if self.flag == 1:
            QMessageBox.information(self, '脑电数据信息', str(self.raw.info))
        else:
            QMessageBox.warning(self, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)

    def Preprocess_slot(self):
        # 判断数据是否已经读入
        if self.flag == 1:
            self.select = QMainWindow()
            self.select.setWindowTitle("预处理选择")
            self.select.setGeometry(100, 100, 400, 300)
            select1 = QPushButton("脑电数据的裁剪", self.select)
            select1.clicked.connect(self.Preprocess1)
            select2 = QPushButton("坏道的去除", self.select)
            select2.clicked.connect(self.Preprocess2)
            select3 = QPushButton("重新设置采样频率", self.select)
            select3.clicked.connect(self.Preprocess3)
            layout = QVBoxLayout()
            layout.addWidget(select1)
            layout.addWidget(select2)
            layout.addWidget(select3)
            central_widget = QWidget()
            central_widget.setLayout(layout)
            self.select.setCentralWidget(central_widget)
            self.select.show()
        else:
            QMessageBox.warning(self, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def Preprocess1(self):
        if self.flag == 1:
            self.select.hide()
            self.preprocess1 = QWidget()
            self.preprocess1.setWindowTitle("脑电数据的裁剪")
            layout = QVBoxLayout()
            # 起始时间布局
            start_layout = QHBoxLayout()
            self.preprocess1.start_label = QLabel('起始时间:')
            self.preprocess1.start_edit = QLineEdit()
            start_layout.addWidget(self.preprocess1.start_label)
            start_layout.addWidget(self.preprocess1.start_edit)
            layout.addLayout(start_layout)
            # 终止时间布局
            end_layout = QHBoxLayout()
            self.preprocess1.end_label = QLabel('终止时间:')
            self.preprocess1.end_edit = QLineEdit()
            end_layout.addWidget(self.preprocess1.end_label)
            end_layout.addWidget(self.preprocess1.end_edit)
            layout.addLayout(end_layout)
            # 确认按钮
            self.preprocess1.confirm_button = QPushButton('确认')
            layout.addWidget(self.preprocess1.confirm_button)
            self.preprocess1.setLayout(layout)
            self.preprocess1.show()
            self.preprocess1.confirm_button.clicked.connect(self.cropslot)
        else:
            #警告信息
            QMessageBox.warning(self, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def cropslot(self):
        t1 = float(self.preprocess1.start_edit.text())
        t2 = float(self.preprocess1.end_edit.text())
        self.preprocess1.hide()
        self.raw.crop(tmin = t1, tmax = t2)
        QMessageBox.information(self, '数据裁剪', '数据已保存')
        self.showgraph_raw()

    def Preprocess2(self):
        pass

    def Preprocess3(self):
        pass

    def process_slot(self):
        if self.flag == 1:
            print("正在进行数据处理...")
            self.select = QMainWindow()
            self.select.setWindowTitle("选择参考方式")
            self.select.setGeometry(100, 100, 400, 300)
            select1 = QPushButton("设置单个电极为参考电极", self.select)
            select1.clicked.connect(self.set_reference)
            select2 = QPushButton("平均参考(AR)", self.select)
            select2.clicked.connect(self.set_AR)
            select3 = QPushButton("REST", self.select)
            select3.clicked.connect(self.set_REST)
            # 创建布局
            layout = QVBoxLayout()
            layout.addWidget(select1)
            layout.addWidget(select2)
            layout.addWidget(select3)
            central_widget = QWidget()
            central_widget.setLayout(layout)
            self.select.setCentralWidget(central_widget)
            self.select.show()
        else:
            QMessageBox.warning(self, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def showgraph_raw(self):
        scene = QGraphicsScene()
        # 在MNE中绘制原始数据并保存为图片
        fig = self.raw.plot(show=False)
        fig.savefig('raw_data_plot.png', bbox_inches='tight', pad_inches=0)  # 调整设置以确保保存完整的图像
        plt.close(fig)
        # 加载保存的图片
        pixmap = QPixmap('raw_data_plot.png')
        # 创建GraphicsPixmapItem并添加到Graphics Scene中
        pixmap_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(pixmap_item)
        self.graph1.setScene(scene)
        self.graph1.show()

    def showgraph_raw_after(self):
        scene = QGraphicsScene()
        # 在MNE中绘制原始数据并保存为图片
        fig = self.raw_after.plot(show=False)
        fig.savefig('raw_avg_ref_data_plot.png', bbox_inches='tight', pad_inches=0)  # 调整设置以确保保存完整的图像
        plt.close(fig)
        # 加载保存的图片
        pixmap = QPixmap('raw_avg_ref_data_plot.png')
        # 创建GraphicsPixmapItem并添加到Graphics Scene中
        pixmap_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(pixmap_item)
        self.graph2.setScene(scene)
        self.graph2.show()

    def set_reference(self):
        if self.flag == 1:
            self.select = QWidget()
            self.select.setWindowTitle("选择参考电极:")
            layout = QVBoxLayout()
            self.select.cb = QComboBox()
            self.select.cb.addItems(self.raw.info['ch_names'])
            self.select.pb = QPushButton()
            self.select.pb.setText("确定")
            layout.addWidget(self.select.cb)
            layout.addWidget(self.select.pb)
            self.select.setLayout(layout)
            self.select.show()
            self.select.pb.clicked.connect(self.setslot)
            self.flag2 = 1
            # self.reference标记当前参考方式
            self.reference = 1
        else:
            QMessageBox.warning(self, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def setslot(self):
        print("正在转换参考...")
        self.select.hide()
        self.channel = self.select.cb.currentText()
        channel_chosed = list()
        channel_chosed.append(self.channel)
        print(channel_chosed)
        raw_set_ref = self.raw.copy().set_eeg_reference(ref_channels = channel_chosed)
        raw_set_ref.plot()
        _translate = QtCore.QCoreApplication.translate
        self.text1.setText("转换方式：单个电极("+self.channel+")")
        self.raw_after = raw_set_ref
        self.showgraph_raw_after()

    def set_AR(self):
        if self.flag == 1:
            print("正在转换为平均参考...")
            raw_avg_ref = self.raw.copy().set_eeg_reference(ref_channels="average", projection=True)  # 设置平均参考
            raw_avg_ref.plot()
            _translate = QtCore.QCoreApplication.translate
            self.text1.setText("转换方式:AR")
            self.raw_after = raw_avg_ref
            self.flag2 = 1
            self.reference = 2
            self.showgraph_raw_after()
        else:
            QMessageBox.warning(self, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def set_REST(self):
        if self.flag == 1:
            print("正在转换为REST参考...")
            self.raw.load_data()  # 裁剪时间从0-60的片段
            sphere = mne.make_sphere_model("auto", "auto", self.raw.info)
            src = mne.setup_volume_source_space(sphere=sphere, exclude=30.0, pos=15.0)
            forward = mne.make_forward_solution(self.raw.info, trans=None, src=src, bem=sphere)
            raw_rest = self.raw.copy().set_eeg_reference("REST", forward=forward)
            raw_rest.plot()
            _translate = QtCore.QCoreApplication.translate
            self.text1.setText("转换方式:REST")
            self.raw_after = raw_rest
            plt.show()
            self.flag2 = 1
            self.reference = 3
            self.showgraph_raw_after()
        else:
            QMessageBox.warning(self, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def quick_save_slot(self):
        if self.flag == 1:
            if self.reference == 1:
                self.after_path = self.file_path[0:-4] + '_SET_raw.fif'
                self.raw.save("sample/Sample_of_EEG_file_with_xyz_channel_location_raw.fif")
            elif self.reference == 2:
                self.after_path = self.file_path[0:-4] + '_AR_raw.fif'
                self.raw.save("sample/Sample_of_EEG_file_with_xyz_channel_location_raw.fif")
            elif self.reference == 3:
                self.after_path = self.file_path[0:-4] + '_REST_raw.fif'
                self.raw.save("sample/Sample_of_EEG_file_with_xyz_channel_location_raw.fif")
        else:
            QMessageBox.warning(self, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def save_slot(self):
        pass

    def details_slot1(self):
        if self.flag == 1:
            self.raw.plot()
        else:
            QMessageBox.warning(self, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def details_slot2(self):
        if self.flag == 1:
            if self.flag2 == 1:
                self.raw_after.plot()
            else:
                QMessageBox.warning(self, '警告', '请先进行参考转换', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            QMessageBox.warning(self, '警告', '请先读入数据', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    warnings.filterwarnings("ignore")
    myWin = MyWin()
    myWin.show()
    sys.exit(app.exec_())