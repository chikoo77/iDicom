import os
from PyQt4 import QtCore, QtGui
from iDicom import iDicom
from MainWindow_ui import Ui_MainWindow


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.dicomVisWidget = iDicom()
        self.ui.verticalLayout.insertWidget(0, self.dicomVisWidget)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        studyPath = str(os.path.join(dir_path, 'images'))
        self.dicomVisWidget.load_study_from_path(studyPath)

    @QtCore.pyqtSlot()
    def on_loadStudyBtn_clicked(self):
        dicompath = str(QtGui.QFileDialog.getExistingDirectory(None, "Open Directory", "/home", QtGui.QFileDialog.ShowDirsOnly))
        try:
            self.dicomVisWidget.load_study_from_path(dicompath)
        except:
            infobox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Error", "Something went wrong =/")
            infobox.exec_()


    @QtCore.pyqtSlot()
    def on_actionAbout_triggered(self):
        infobox = QtGui.QMessageBox(QtGui.QMessageBox.Information, "About", "iDicom 2017")
        infobox.exec_()
        
    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        dicompath = str(QtGui.QFileDialog.getExistingDirectory(None, 'Open Directory', '/home', QtGui.QFileDialog.ShowDirsOnly))
        try:
            self.dicomVisWidget.load_study_from_path(dicompath)
        except:
            infobox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Error', 'Something went wrong =/')
            infobox.exec_()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    exitCode = app.exec_()
    sys.exit(exitCode)


