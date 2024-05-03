import sys
from PyQt5.QtWidgets import *
from controller import MY_Controller

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MY_sys = MY_Controller()
    # 读取qss样式表
    with open('DIY.qss', 'r') as f:
        app.setStyleSheet(f.read())
    sys.exit(app.exec_())
