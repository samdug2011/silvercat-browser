import sys
 
from PyQt5.QtWidgets import QApplication
 
from main import *
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('logo.png'))
    MainWindow = BrowserWindow()
    MainWindow.showMaximized()
    sys.exit(app.exec_())