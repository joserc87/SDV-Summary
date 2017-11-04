import sys
import time
import json
import os
import ctypes

from PySide import QtGui, QtCore, QtWebKit
from tendo import singleton

from webserver import launch_webserver_as_process
from loopbacklistener import launch_loopback, check_app_running
from watcher import launch_watcher_as_thread
from database import (check_settings, get_current_savegame_filenames, set_monitors, get_monitors,
				update_monitor, is_user_info_invalid, clear_user_info, get_latest_log_entry_for,
				get_user_info, set_user_info)
from watcherlib import Watcher, manual_process
from config import server_location, client_id, backup_directory
from ufapi import get_user_email
from uploadmonitor import launch_uploadmonitor_as_thread
from multiprocessing import freeze_support
from addtoregistry import add_to_startup, remove_from_startup, check_startup
from setup import version
from versioninfo import version_is_current

AUTHENTICATION_URL = server_location+"/auth?client_id="+client_id
ACCOUNT_URL = server_location+"/acc"
BACKUP_DIRECTORY = backup_directory
RUN_STARDEW_VALLEY_STEAM = 'steam://rungameid/413150'
__version__ = version

class WebWindow(QtGui.QWidget):
	def __init__(self,url,title='Help'):
		super().__init__()
		self.view = QtWebKit.QWebView(self)
		self.view.load(url)

		self.layout = QtGui.QHBoxLayout()
		self.layout.addWidget(self.view)
		self.setWindowIcon(QtGui.QIcon('icons/windows_icon.ico'))

		self.setLayout(self.layout)
		self.resize(800,600)
		self.setWindowTitle(title)
		self.show()

class WaitingWindow(QtGui.QMainWindow):
	def __init__(self):
		super().__init__()
		remove_from_startup()
		self.webserver = launch_webserver_as_process()
		self.init_ui()
		self.set_bg_image()
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.check_db)
		self.timer.start(1000)
		self.fully_kill = True


	aboutToQuit = QtCore.Signal()


	def set_bg_image(self):
		self.bgimage = QtGui.QPixmap("images/bg.png").scaled(self.size(), transformMode=QtCore.Qt.SmoothTransformation)
		palette = QtGui.QPalette()
		palette.setBrush(QtGui.QPalette.Window,self.bgimage)
		self.setPalette(palette)


	def resizeEvent(self,event):
		self.set_bg_image()
		event.accept()


	def init_ui(self):
		self.name_of_application = "upload.farm uploader v{}".format(__version__)
		self.setWindowTitle(self.name_of_application)
		self.setWindowIcon(QtGui.QIcon('icons/windows_icon.ico'))
		self._create_layouts_and_widgets()
		self.show()


	def _create_layouts_and_widgets(self):
		self._logo = QtGui.QLabel()
		self._logo.setPixmap(QtGui.QPixmap("images/logo.png"))

		self._explanation = QtGui.QTextEdit("This tool is a thank-you to supporters of "
			"upload.farm.<br><br>It allows you to automatically backup your Stardew Valley "
			"savegames and upload them to upload.farm for safekeeping.<br><br>To begin using "
			"the uploader, please authenticate with your upload.farm account by pressing "
			"the button below, or by navigating to:<br><br>{}".format(AUTHENTICATION_URL))
		self._explanation.setReadOnly(True)
		self._profile_button = QtGui.QPushButton("&Authenticate")
		self._profile_button.clicked.connect(self.open_api_auth)
		self._help_button = QtGui.QPushButton("&Help!")
		self._help_button.clicked.connect(self.open_help)

		self._vbox = QtGui.QVBoxLayout()
		self._vbox.addStretch(1)
		logobox = QtGui.QHBoxLayout()
		logobox.addStretch(1)
		logobox.addWidget(self._logo)
		logobox.addStretch(1)
		self._vbox.addLayout(logobox)
		self._vbox.addStretch(1)
		logobox = QtGui.QHBoxLayout()
		logobox.addStretch(1)
		logobox.addWidget(self._explanation)
		logobox.addStretch(1)
		self._vbox.addLayout(logobox)
		self._vbox.addStretch(1)
		logobox = QtGui.QHBoxLayout()
		logobox.addStretch(1)
		logobox.addWidget(self._profile_button)
		logobox.addWidget(self._help_button)
		logobox.addStretch(1)
		self._vbox.addLayout(logobox)
		self._vbox.addStretch(1)

		self._main_widget = QtGui.QWidget()
		self._main_widget.setLayout(self._vbox)
		self._main_widget.setMinimumWidth(500)
		self._main_widget.setMinimumHeight(400)
		self.setCentralWidget(self._main_widget)


	def open_api_auth(self):
		QtGui.QDesktopServices.openUrl(AUTHENTICATION_URL)


	def check_db(self):
		if check_settings() == True and is_user_info_invalid() == False:
			time.sleep(0.2)
			self.caught_credentials()


	def caught_credentials(self):
		# print('killing webserver')
		self.timer.stop()
		self.webserver.terminate()
		add_to_startup()
		self.main_window = MainWindow()
		self.main_window.activateWindow()
		self.main_window.raise_()
		self.main_window.setParent(self.parent())
		try:
			self.help_window.close()
		except:
			pass
		self.hide()
		self.fully_kill = False
		self.close()
		

	def open_help(self):
		self.help_window = WebWindow("help/help.html")
		self.help_window.hide()
		self.aboutToQuit.connect(self.help_window.close)
		self.help_window.show()


	def closeEvent(self,event):
		self.webserver.terminate()
		try:
			self.help_window.close()
		except:
			pass
		if self.fully_kill:
			QtCore.QCoreApplication.instance().quit()
		event.accept()


class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		super().__init__()
		self.init_ui()
		self.init_tray()
		self.set_bg_image()
		set_monitors()
		self.run_watcher()
		self.run_uploadmonitor()
		self.updateGui.connect(self.update_gui)
		self.authError.connect(self.handle_auth_error)
		self.maximizeWindow.connect(self.activate_main_window)
		self.run_loopback()
		self._last_updated = 0
		self.update_gui()
		if is_user_info_invalid():
			self.reauthorise()
		elif not(len(sys.argv)>1 and sys.argv[1] == '--silent'):
			self.show()

	updateGui = QtCore.Signal()
	aboutToQuit = QtCore.Signal()
	authError = QtCore.Signal()
	maximizeWindow = QtCore.Signal()


	def run_loopback(self):
		self.loopback = launch_loopback(self.maximizeWindow)


	def run_watcher(self):
		self._watcher = launch_watcher_as_thread(BACKUP_DIRECTORY,self.updateGui)


	def run_uploadmonitor(self):
		self._uploadmonitor = launch_uploadmonitor_as_thread(error_signal=self.authError,update_signal=self.updateGui)


	def set_bg_image(self):
		self.bgimage = QtGui.QPixmap("images/bg.png").scaled(self.size(), transformMode=QtCore.Qt.SmoothTransformation)
		palette = QtGui.QPalette()
		palette.setBrush(QtGui.QPalette.Window,self.bgimage)
		self.setPalette(palette)


	def resizeEvent(self,event):
		self.set_bg_image()
		event.accept()


	def init_ui(self):
		self.name_of_application = "upload.farm uploader v{}".format(__version__)
		self.add_email_to_application_name()
		self.setWindowTitle(self.name_of_application)
		self.setWindowIcon(QtGui.QIcon('icons/windows_icon.ico'))
		self._create_layouts_and_widgets()


	def add_email_to_application_name(self):
		try:
			email = get_user_info()[1]
			if email == None:
				email = get_user_email()['email']
				set_user_info({'email':email})
			self.name_of_application += ' - {}'.format(email)
		except:
			pass


	def init_tray(self):
		self._popup_shown = False
		self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon("icons/windows_icon.ico"),self)
		self.trayIconMenu = QtGui.QMenu()

		self.openAction = QtGui.QAction("&Show/Hide", self, triggered=self._showhide)
		self.startupAction = QtGui.QAction("Start &Automatically", self, triggered=self.toggle_startup)
		self.exitAction = QtGui.QAction("&Exit", self, triggered=self._icon_exit)

		self.startupAction.setCheckable(True)
		self.startupAction.setChecked(check_startup())

		self.trayIconMenu.addAction(self.openAction)
		self.trayIconMenu.addSeparator()
		self.trayIconMenu.addAction(self.startupAction)
		self.trayIconMenu.addSeparator()
		self.trayIconMenu.addAction(self.exitAction)

		self.trayIcon.setContextMenu(self.trayIconMenu)
		self.trayIcon.activated.connect(self._icon_activated)
		self._show_when_systray_available()


	def _show_when_systray_available(self):
		if self.trayIcon.isSystemTrayAvailable():
			self.trayIcon.show()
		else:
			QtCore.QTimer.singleShot(1000,self._show_when_systray_available)


	def _create_layouts_and_widgets(self):
		self._table_layout = QtGui.QGridLayout()
		self._table = QtGui.QTableWidget(0,6,self)
		self._table_header = QtGui.QHeaderView(QtCore.Qt.Orientation.Horizontal)
		self._table_header.setResizeMode(QtGui.QHeaderView.ResizeToContents)
		# self._table_header.stretchLastSection()
		self._table.setHorizontalHeader(self._table_header)
		self._table.setHorizontalHeaderLabels(['Savegame','Last backed up','Auto\nbackup','Upload\nbackups','Manual\nbackup','Latest URL'])
		self._table.itemClicked.connect(self.item_clicked_handler)

		self._logo = QtGui.QLabel()
		self._logo.setPixmap(QtGui.QPixmap("images/logo.png"))
		self._profile_button = QtGui.QPushButton("&My Account")
		self._profile_button.clicked.connect(self.open_acc_page)
		self._run_sdv_button = QtGui.QPushButton("Launch &Game!")
		self._run_sdv_button.clicked.connect(self.run_stardew_valley)
		self._browse_button = QtGui.QPushButton("&Backups")
		self._browse_button.clicked.connect(self.open_browse_backups)
		self._logout_button = QtGui.QPushButton("&Logout")
		self._logout_button.clicked.connect(self._logout)
		self._exit_button = QtGui.QPushButton("E&xit")
		self._exit_button.clicked.connect(self._icon_exit)
		self._help_button = QtGui.QPushButton("&Help")
		self._help_button.clicked.connect(self.open_help)
		self._update_button = QtGui.QPushButton("&Updates")
		self._update_button.clicked.connect(self.check_for_update)

		self._table_layout.addWidget(self._table)

		self._vbox = QtGui.QVBoxLayout()
		self._hbox_title = QtGui.QHBoxLayout()
		self._vbox_title = QtGui.QVBoxLayout()
		self._menubar = QtGui.QHBoxLayout()

		self._hbox_title.addWidget(self._logo)
		self._hbox_title.addStretch(1)
		self._hbox_title.addLayout(self._vbox_title)
		self._vbox_title.addLayout(self._menubar)
		self._vbox_title.setAlignment(QtCore.Qt.AlignTop)
		self._menubar.addWidget(self._profile_button)
		self._menubar.addWidget(self._run_sdv_button)
		self._menubar.addWidget(self._browse_button)
		self._menubar.addWidget(self._logout_button)
		self._menubar.addWidget(self._exit_button)
		self._menubar.addWidget(self._help_button)
		self._menubar.addWidget(self._update_button)
		self._vbox.addLayout(self._hbox_title)
		self._vbox.addLayout(self._table_layout)

		self._main_widget = QtGui.QWidget()
		self._main_widget.setLayout(self._vbox)
		self._main_widget.setMinimumWidth(700)
		self._main_widget.setMinimumHeight(500)
		self.setCentralWidget(self._main_widget)


	def check_for_update(self):
		if not version_is_current():
			QtGui.QMessageBox.information(self,"upload.farm uploader","There is a new version of this tool! Please visit <a href='{}'>upload.farm</a> to download!".format(server_location))
		else:
			QtGui.QMessageBox.information(self,"upload.farm uploader","Your uploader version appears up-to-date!")			

	def update_gui(self):
		"""activates on Signal, updates GUI table from db"""
		if time.time() - self._last_updated > 0.1:
			self._last_updated = time.time()
			self._raw_db_output = get_monitors()
			self.populate_table()
		

	def toggle_startup(self):
		if check_startup() == True:
			remove_from_startup()
		else:
			add_to_startup()
		return check_startup()


	def populate_table(self):
		"""takes db data, compares with internal state,
		_add_table_row's or _remove_table_row's as required"""
		self._table_state = []
		self._clear_table()
		for item in self._raw_db_output:
			try:
				info = json.loads(item[2])
				datestring = info['date']
			except:
				info = []
				datestring = None
			j, uploadable, uploaded = get_latest_log_entry_for(item[0],successfully_uploaded=True)
			url = j.get('url','...' if uploadable and not uploaded else None)
			row = [item[0],datestring,True if item[4]==1 else False,True if item[5]==1 else False,None,url]
			self._table_state.append(row)
			self._add_table_row(row)


	def _clear_table(self):
		for i in reversed(range(self._table.rowCount())):
			self._remove_table_row(i)


	def _remove_table_row(self,row_id):
		self._table.removeRow(row_id)


	def _add_table_row(self,items):
		new_row = self._table.rowCount()+1
		self._table.setRowCount(new_row)
		for i, item in enumerate(items):
			if type(item) != bool:
				if i == 4:
					self.new_item = QtGui.QPushButton('Backup!')
					self.new_item.clicked.connect(self.handle_manual_backup)
					self._table.setCellWidget(new_row-1,i,self.new_item)
					continue
				elif i == 5 and item != None:
					if item != '...':
						new_item = QtGui.QTableWidgetItem('{}'.format(item))
						link_font = QtGui.QFont(new_item.font())
						link_font.setUnderline(True)
						new_item.setFont(link_font)
						new_item.setTextAlignment(QtCore.Qt.AlignCenter)
						new_item.setForeground(QtGui.QBrush(QtGui.QColor("teal")))
					else:
						new_item = QtGui.QTableWidgetItem('{}'.format(item))
						new_item.setTextAlignment(QtCore.Qt.AlignCenter)
				elif i == 1 and item == None:
					new_item = QtGui.QTableWidgetItem('no backups')
					new_item.setForeground(QtGui.QBrush(QtGui.QColor("grey")))
				else:
					new_item = QtGui.QTableWidgetItem(item)
				new_item.setFlags(QtCore.Qt.ItemIsEnabled)
			elif type(item) == bool:
				new_item = QtGui.QTableWidgetItem()
				if i == 3 and items[2] == False:
					new_item.setFlags(QtCore.Qt.ItemFlags() != QtCore.Qt.ItemIsEnabled)
					new_item.setCheckState(QtCore.Qt.Unchecked)
				else:
					new_item.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
					new_item.setCheckState(QtCore.Qt.Unchecked if item == False else QtCore.Qt.Checked)
			self._table.setItem(new_row-1,i,new_item)


	def item_clicked_handler(self, item):
		column_fieldname = {2:'monitoring',3:'uploading'}
		if item.column() in column_fieldname:
			if item.checkState() == QtCore.Qt.Checked:
				checkstate = True
			elif item.checkState() == QtCore.Qt.Unchecked:
				checkstate = False
			if checkstate != self._table_state[item.row()][item.column()]:
				if item.column() == 2:
					update_monitor(self._table_state[item.row()][0],monitoring=checkstate)
					if checkstate == True:
						self._table.item(item.row(),3).setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
					else:
						self._table.item(item.row(),3).setFlags(QtCore.Qt.ItemFlags() != QtCore.Qt.ItemIsEnabled)
						self._table.item(item.row(),3).setCheckState(QtCore.Qt.Unchecked)
				elif item.column() == 3:
					update_monitor(self._table_state[item.row()][0],uploading=checkstate)
				self._table_state[item.row()][item.column()] = checkstate
		if item.column() == 5:
			if self._table_state[item.row()][item.column()] != None:
				QtGui.QDesktopServices.openUrl(server_location+'/'+self._table_state[item.row()][item.column()])


	def handle_manual_backup(self):
		button = QtGui.qApp.focusWidget()
		index = self._table.indexAt(button.pos())
		if index.isValid():
			manual_process(self._table_state[index.row()][0],BACKUP_DIRECTORY)
			self.update_gui()


	def _icon_exit(self):
		self.set_okayToClose(True)
		self.close()


	def set_okayToClose(self,value):
		self._okaytoclose = value


	def okayToClose(self):
		try:
			if self._okaytoclose == True:
				return True
			else:
				return False
		except:
			return False


	def closeEvent(self,event):
		if self.okayToClose():
			self.trayIcon.hide()
			self.aboutToQuit.emit()
			QtCore.QCoreApplication.instance().quit()
			event.accept()
		else:
			self.hide()
			if self.trayIcon.isVisible() and self._popup_shown != True:
				self._popup_shown = True
				# QtGui.QMessageBox.information(self,"upload.farm uploader","The uploader will keep running in the system tray. To fully terminate the program, right-click the icon in the system tray and choose <b>Exit</b>.")
				reply = QtGui.QMessageBox.question(self,'upload.farm uploader','Do you want the uploader to keep running in the system tray?'
					' This is a good option if you want to keep it monitoring your Stardew Valley savegames!', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
				if reply == QtGui.QMessageBox.No:
					QtCore.QCoreApplication.instance().quit()
					event.accept()
			event.ignore()


	def open_acc_page(self):
		QtGui.QDesktopServices.openUrl(ACCOUNT_URL)


	def open_browse_backups(self):
		os.startfile(BACKUP_DIRECTORY)


	def open_help(self):
		self.help_window = WebWindow("help/help.html")
		self.help_window.hide()
		self.aboutToQuit.connect(self.help_window.close)
		self.help_window.show()


	def _icon_activated(self,reason):
		if reason == QtGui.QSystemTrayIcon.DoubleClick:
			self.activate_main_window()


	def _showhide(self):
		if not self.isVisible():
			self.activate_main_window()
		else:
			self.hide()


	def activate_main_window(self):
		self.show()
		self.activateWindow()


	def _logout(self):
		reply = QtGui.QMessageBox.question(self,'Really logout?','Are you sure you want to log out? Your API credentials will be deleted'
			' and you will have to re-authorise with upload.farm to continue using the uploader!', QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
		if reply == QtGui.QMessageBox.Yes:
			clear_user_info()
			self.handle_auth_error()


	def handle_auth_error(self):
		self.reauthorise()


	def reauthorise(self):
		QtGui.QMessageBox.information(self, "Re-authorisation needed!",
				"You must re-authorise the uploader to continue using this application.")
		self.hide()
		self.auth_window = WaitingWindow()
		self.auth_window.setParent(self.parent())


	def run_stardew_valley(self):
		os.startfile(RUN_STARDEW_VALLEY_STEAM)


def windows_appusermodelid():
	myappid = 'UploadFarm.Uploader.0001'
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


def launch():
	freeze_support()
	check_app_running()
	me = singleton.SingleInstance()
	windows_appusermodelid()
	app = QtGui.QApplication(sys.argv)
	QtGui.QApplication.setQuitOnLastWindowClosed(False)
	if check_settings() == False or is_user_info_invalid() == True:
		waiting = WaitingWindow()
	else:
		main = MainWindow()
	sys.exit(app.exec_())


if __name__ == "__main__":
	launch()