#!/usr/bin/env python
# coding=utf-8

import os
import platform
import sys

from PyQt4 import QtCore, QtGui

from helpform.helpform import HelpForm
from ui.mainwindow import Ui_MainWindow
from player.player import Player

RECORDING_STYLE = """
    QPushButton {
        background-color: red;
    }
    QPushButton:pressed {
        background-color: red;
    }
"""

__version__ = "1.0.0"


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """

    :param parent:
    """

    def __init__(self, parent=None):
        """

        :param parent:
        """
        super(MainWindow, self).__init__(parent)

        self.dirty = False
        self.filename = None
        self.image = None
        self.player = Player()

        self.setupUi(self)
        self.statusbar.showMessage("Ready", 5000)
        self.action_About.triggered.connect(self.helpabout)
        self.action_Save.setShortcut(QtGui.QKeySequence.Save)
        self.actionSave_As.setShortcut(QtGui.QKeySequence.SaveAs)
        self.action_Quit.triggered.connect(self.close)
        self.action_Quit.setShortcut(QtGui.QKeySequence.Quit)
        self.action_Help.triggered.connect(self.helphelp)
        self.action_Help.setShortcut(QtGui.QKeySequence.HelpContents)

        self.pushButton.clicked.connect(self.on_button_clicked)
        self.pushButton_2.clicked.connect(self.on_button_2_clicked)

        settings = QtCore.QSettings()
        self.recentfiles = settings.value("RecentFiles").toStringList()
        self.restoreGeometry(settings.value("MainWindow/Geometry").toByteArray())
        self.restoreState(settings.value("MainWindow/State").toByteArray())

        QtCore.QTimer.singleShot(0, self.loadinitialfile)

    def closeEvent(self, event):
        """

        :param event:
        """
        if self.oktocontinue():
            settings = QtCore.QSettings()
            filename = (QtCore.QVariant(QtCore.QString(self.filename))
                        if self.filename is not None else QtCore.QVariant())
            settings.setValue("LastFile", filename)
            recentfiles = (QtCore.QVariant(self.recentfiles)
                           if self.recentfiles else QtCore.QVariant())
            settings.setValue("RecentFiles", recentfiles)
            settings.setValue("MainWindow/Geometry", QtCore.QVariant(
                self.saveGeometry()))
            settings.setValue("MainWindow/State", QtCore.QVariant(
                self.saveState()))
        else:
            event.ignore()

    def oktocontinue(self):
        """


        :return:
        """
        if self.dirty:
            reply = QtGui.QMessageBox.question(self, "Image Changer - Unsaved Changes", "Save unsaved changes?",
                                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                return False
            elif reply == QtGui.QMessageBox.Yes:
                return self.filesave()
        return True

    def loadinitialfile(self):
        settings = QtCore.QSettings()
        fname = unicode(settings.value("LastFile").toString())
        if fname and QtCore.QFile.exists(fname):
            self.loadfile(fname)

    def updatestatus(self, message):
        """

        :param message:
        """
        self.statusBar().showMessage(message, 5000)
        self.listWidget.addItem(message)
        if self.filename is not None:
            self.setWindowTitle("Image Changer - {0}[*]".format(
                os.path.basename(self.filename)))
        elif not self.image.isNull():
            self.setWindowTitle("Image Changer - Unnamed[*]")
        else:
            self.setWindowTitle("Image Changer[*]")
        self.setWindowModified(self.dirty)

    def loadfile(self, fname=None):
        """

        :param fname:
        :return:
        """
        if fname is None:
            action = self.sender()
            if isinstance(action, QtGui.QAction):
                fname = unicode(action.data().toString())
                if not self.oktocontinue():
                    return
            else:
                return
        if fname:
            self.filename = None
            image = QtGui.QImage(fname)
            if image.isNull():
                message = "Failed to read {0}".format(fname)
            else:
                self.addRecentFile(fname)
                self.image = QtGui.QImage()
                self.image = image
                self.filename = fname
                self.showImage()
                self.dirty = False
                self.sizeLabel.setText("{0} x {1}".format(image.width(), image.height()))
                message = "Loaded {0}".format(os.path.basename(fname))
            self.updatestatus(message)

    def filesave(self):
        """


        :return:
        """
        if self.image.isNull():
            return True
        if self.filename is None:
            return self.filesaveas()
        else:
            if self.image.save(self.filename, None):
                self.updatestatus("Saved as {0}".format(self.filename))
                self.dirty = False
                return True
            else:
                self.updatestatus("Failed to save {0}".format(self.filename))
                return False

    def filesaveas(self):
        """


        :return:
        """
        if self.image.isNull():
            return True
        fname = self.filename if self.filename is not None else "."
        formats = (["*.{0}".format(unicode(format).lower())
                    for format in QtGui.QImageWriter.supportedImageFormats()])
        fname = unicode(QtGui.QFileDialog.getSaveFileName(self,
                                                          "Image Changer - Save Image", fname,
                                                          "Image files ({0})".format(" ".join(formats))))
        if fname:
            if "." not in fname:
                fname += ".png"
            self.addRecentFile(fname)
            self.filename = fname
            return self.filesave()
        return False

    def helpabout(self):
        QtGui.QMessageBox.about(self, "About Image Changer",
                                """<b>Image Changer</b> v {0}
                                <p>Copyright &copy; 2008 Qtrac Ltd.
                                All rights reserved.
                                <p>This application can be used to perform
                                simple image manipulations.
                                <p>Python {1} - Qt {2} - PyQt {3} on {4}""".format(__version__,
                                                                                   platform.python_version(),
                                                                                   QtCore.QT_VERSION_STR,
                                                                                   QtCore.PYQT_VERSION_STR,
                                                                                   platform.system()))

    def helphelp(self):
        form = HelpForm("index.html", self)
        form.show()

    def on_button_clicked(self):
        if not self.pushButton.isChecked():
            self.pushButton.setText(QtCore.QString("Resume\n Recording"))
            self.pushButton.setStyleSheet(RECORDING_STYLE)
            self.player.pause()
        elif self.pushButton.isChecked():
            self.pushButton.setText(QtCore.QString("Pause"))
            self.pushButton.setStyleSheet(RECORDING_STYLE)
            self.player.play()

    def on_button_2_clicked(self):
        self.pushButton.setStyleSheet("")
        self.pushButton.setChecked(False)
        self.pushButton.setText(QtCore.QString("Record"))
        self.player.stop()


def main():
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("Image Changer")
    app.setWindowIcon(QtGui.QIcon(":/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()


main()