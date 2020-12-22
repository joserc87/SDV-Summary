import os
import sys
import ctypes

from PyQt5 import QtGui, QtCore, QtWidgets  # QtWebEngineWidgets
from PIL import ImageQt

from moreplayers import SaveGame, new_cabin

QWidget = QtWidgets.QWidget
QMainWindow = QtWidgets.QMainWindow
Signal = QtCore.pyqtSignal
QApplication = QtWidgets.QApplication
QLabel = QtWidgets.QLabel
QHBoxLayout = QtWidgets.QHBoxLayout
QVBoxLayout = QtWidgets.QVBoxLayout
QTextEdit = QtWidgets.QTextEdit
QCheckBox = QtWidgets.QCheckBox
QDoubleSpinBox = QtWidgets.QDoubleSpinBox
QPushButton = QtWidgets.QPushButton
QGridLayout = QtWidgets.QGridLayout
QHeaderView = QtWidgets.QHeaderView
QSystemTrayIcon = QtWidgets.QSystemTrayIcon
QMenu = QtWidgets.QMenu
QAction = QtWidgets.QAction
QTableWidget = QtWidgets.QTableWidget
QMessageBox = QtWidgets.QMessageBox
QSlider = QtWidgets.QSlider
QTableWidgetItem = QtWidgets.QTableWidgetItem
qApp = QtWidgets.qApp
QUrl = QtCore.QUrl
QThreadPool = QtCore.QThreadPool

LOGO_ICON = "images/logo.png"
HELP_FILE_LOCATION = "file:///{}".format(os.path.abspath("help/help.html"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.set_bg_image()
        self.savegame = None
        # self.timer = QtCore.QTimer(self)
        # self.timer.start(1000)

    def set_bg_image(self):
        self.bgimage = QtGui.QImage("images/bg.png").scaled(
            self.size(), transformMode=QtCore.Qt.SmoothTransformation
        )
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(self.bgimage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_bg_image()
        event.accept()

    def init_ui(self):
        self.name_of_application = "RoboRobin by upload.farm"
        self.setWindowTitle(self.name_of_application)
        self.setWindowIcon(QtGui.QIcon("images/icon.ico"))
        self._create_layouts_and_widgets()
        self.show()

    def _create_layouts_and_widgets(self):
        self._logo = QLabel()
        self._logo.setPixmap(QtGui.QPixmap(LOGO_ICON))

        self._explanation = QLabel(
            "This tool allows you to modify your v1.3+ Stardew Valley savegame to add extra cabins."
            " By using this software you acknowledge it software comes with no warranty of any kind."
        )
        self._load_button = QPushButton("&Open Save")
        self._load_button.clicked.connect(self.get_file)
        self._help_button = QPushButton("&Help")
        self._help_button.clicked.connect(self.open_help)
        self._save_button = QPushButton("&Write Save")
        self._save_button.clicked.connect(self.save_file)

        self._vbox = QVBoxLayout()
        self._hbox_title = QHBoxLayout()
        self._vbox_title = QVBoxLayout()
        self._menubar = QVBoxLayout()

        self._hbox_title.addWidget(self._logo)
        self._hbox_title.addStretch(1)
        self._hbox_title.addLayout(self._vbox_title)
        self._vbox_title.addLayout(self._menubar)
        self._vbox_title.setAlignment(QtCore.Qt.AlignTop)
        self._menubar.addWidget(self._load_button)
        # self._menubar1.addWidget(self._browse_button)
        # self._menubar1.addWidget(self._launch_gif_button)
        self._menubar.addWidget(self._help_button)
        # self._menubar2.addWidget(self._update_button)
        # self._menubar2.addWidget(self._logout_button)
        self._menubar.addWidget(self._save_button)
        self._vbox.addLayout(self._hbox_title)
        # self._vbox.addLayout(self._table_layout)

        self._grid_hbox = QHBoxLayout()
        self._grid = QGridLayout()
        self._preview_image = QtGui.QPixmap("images/placeholder.png")
        self._preview_image = self._preview_image.scaledToWidth(480)
        self._preview = QLabel()
        self._preview.setPixmap(self._preview_image)
        self._grid.addWidget(self._preview, 0, 0)

        self._xposslider = QSlider(QtCore.Qt.Horizontal)
        self._xposslider.setFixedWidth(480)
        self._xposslider.setMinimum(0)
        self._xposslider.setMaximum(75)
        self._xposslider.setValue(37)
        self._xposslider.sliderReleased.connect(self.sliderchanged)

        self._yposslider = QSlider(QtCore.Qt.Vertical)
        self._yposslider.setFixedHeight(390)
        self._yposslider.setMinimum(0)
        self._yposslider.setValue(31)
        self._yposslider.setMaximum(62)
        self._yposslider.sliderReleased.connect(self.sliderchanged)

        self._grid.addWidget(self._xposslider, 1, 0)
        self._grid.addWidget(self._yposslider, 0, 1)
        self._grid_hbox.addStretch(1)
        self._grid_hbox.addLayout(self._grid)
        self._grid_hbox.addStretch(1)
        self._vbox.addLayout(self._grid_hbox)

        self._add_log_cabin = QPushButton("New &Log Cabin")
        self._add_log_cabin.clicked.connect(self.add_log)
        self._add_stone_cabin = QPushButton("New &Stone Cabin")
        self._add_stone_cabin.clicked.connect(self.add_stone)
        self._add_plank_cabin = QPushButton("New &Plank Cabin")
        self._add_plank_cabin.clicked.connect(self.add_plank)
        self._remove_last_cabin = QPushButton("&Remove Last")
        self._remove_last_cabin.clicked.connect(self.remove_last)
        self._control_button_menu = QHBoxLayout()
        self._control_button_menu.addWidget(self._add_log_cabin)
        self._control_button_menu.addWidget(self._add_stone_cabin)
        self._control_button_menu.addWidget(self._add_plank_cabin)
        self._control_button_menu.addWidget(self._remove_last_cabin)

        self.buttons = [
            self._add_log_cabin,
            self._add_plank_cabin,
            self._add_stone_cabin,
            self._remove_last_cabin,
            self._load_button,
            self._help_button,
            self._save_button,
            self._xposslider,
            self._yposslider,
        ]

        self._menu_hbox = QHBoxLayout()
        self._menu_hbox.addStretch(1)
        self._menu_hbox.addLayout(self._control_button_menu)
        self._menu_hbox.addStretch(1)

        self._vbox.addLayout(self._menu_hbox)

        self._main_widget = QWidget()
        self._main_widget.setLayout(self._vbox)
        self._main_widget.setMinimumWidth(700)
        self._main_widget.setMinimumHeight(600)
        self.setFixedSize(700, 600)

        self.setCentralWidget(self._main_widget)

    def get_file(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Savegame",
            os.path.join(os.getenv("APPDATA"), "StardewValley", "Saves"),
            "All Files (*.*)",
        )[0]
        if self.filename != "":
            try:
                self.savegame = SaveGame(self.filename)
                self.can_edit = self.savegame.v1_3()
                if self.can_edit != True:
                    QMessageBox.information(
                        self,
                        "Not a v1.3 savegame!",
                        "The file {} does not appear to be savegame from Stardew Valley version 1.3 or later. This program will probably crash if you try to modify it! For instructions on how to join the v1.3 beta, <a href='https://stardewvalley.net/stardew-valley-v1-3-beta/'>click here</a>".format(
                            self.filename
                        ),
                    )
                try:
                    del self.nc
                except AttributeError:
                    pass
                self.render_minimap()
            except KeyError:
                QMessageBox.information(
                    self,
                    "Unrecognised file!",
                    "The file {} does not appear to be savegame from Stardew Valley and cannot be loaded. Have you tried to open SaveGameInfo by accident?".format(
                        self.filename
                    ),
                )

    def render_minimap(self):
        for button in self.buttons:
            button.setEnabled(False)
        self.render_filename = self.savegame.render()
        self._preview_image = QtGui.QPixmap(self.render_filename)
        self._preview_image = self._preview_image.scaledToWidth(480)
        self._preview.setPixmap(self._preview_image)
        for button in self.buttons:
            button.setEnabled(True)

    def sliderchanged(self):
        if self.savegame and hasattr(self, "nc"):
            self._remove_last()
            self._add_cabin(self.cabinname)

    def add_log(self):
        self.cabin_type = "Log Cabin"
        self._add_cabin()

    def add_stone(self):
        self.cabin_type = "Stone Cabin"
        self._add_cabin()

    def add_plank(self):
        self.cabin_type = "Plank Cabin"
        self._add_cabin()

    def _add_cabin(self, cabinname=None):
        self.xcoord = self._xposslider.value()
        self.ycoord = 62 - self._yposslider.value()
        try:
            self.cabinname = (
                cabinname if cabinname else self.savegame.get_unique_cabin_name()
            )
            self.nc = new_cabin(
                self.xcoord, self.ycoord, self.cabinname, self.cabin_type
            )
            self.savegame.add_cabin(self.nc)
            self.render_minimap()
        except (TypeError, AttributeError):
            QMessageBox.information(
                self,
                "Error adding cabin!",
                "RoboRobin wasn't able to add a cabin to this savegame. Is it pre-v1.3?",
            )

    def open_help(self):
        QtGui.QDesktopServices.openUrl(QUrl(HELP_FILE_LOCATION))

    def remove_last(self):
        self._remove_last()
        self.render_minimap()

    def _remove_last(self):
        try:
            del self.nc
        except AttributeError:
            pass
        try:
            self.savegame.pop_cabin()
        except AttributeError:
            pass

    def save_file(self):
        if hasattr(self, "filename") and self.filename != None:
            self.savegame.save(self.filename)
            QMessageBox.information(
                self,
                "Saved!",
                "Your modified savegame has been written to {}! A backup of the original is stored in that folder in case you want to undo your changes.".format(
                    self.filename
                ),
            )
        else:
            QMessageBox.information(
                self,
                "No file to save!",
                "You haven't opened a file yet, so there's nothing to write!",
            )

    # def closeEvent(self,event):
    # 	event.accept()


def windows_appusermodelid():
    myappid = "UploadFarm.RoboRobin.0001"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


def launch():
    app = QApplication(sys.argv)
    windows_appusermodelid()
    app.setWindowIcon(QtGui.QIcon("images/icon.ico"))
    m = MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    launch()
