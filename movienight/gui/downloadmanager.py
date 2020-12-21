import json
import logging
import os
from configparser import NoOptionError

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from ..config import config
from ..downloadhandler import delete_file
from ..downloadhandler import download_file_async
from ..downloadhandler import get_next_filename

log = logging.getLogger("movienight")

TITLE = "Download Manager"


class DownloadManager(QtWidgets.QMainWindow):
    def __init__(self, master=None):
        QtWidgets.QMainWindow.__init__(self, master)
        self.setWindowTitle(TITLE)
        self.setGeometry(0, 0, 640, 360)
        self.file_ready = None
        self.reload_needed = False
        self.download_directory = None
        self.widget = None
        self.table = None
        self.delete_button = None
        self.layout = None
        self.button_row = None
        self._next_file = None
        self.files = []

        self.create_ui()
        self._update_table()
        try:
            self.download_directory = config.get("download_directory")
            self._load_files()
        except NoOptionError:
            self.reload_needed = True

    def create_ui(self):
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        self.table = QtWidgets.QTableWidget(0, 2, self)
        self.table.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.verticalHeader().hide()
        self.table.setHorizontalHeaderLabels(["Filename", "Progress"])
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader()
        self.table.setColumnWidth(1, 100)

        self.delete_button = QtWidgets.QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete_file)

        self.button_row = QtWidgets.QHBoxLayout()
        self.button_row.addWidget(self.delete_button)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.table)
        self.layout.addLayout(self.button_row)
        self.widget.setLayout(self.layout)

    def _add_item(self, filename):
        for item in self.files:
            if item[0] == filename:
                log.debug("Item already in list: '%s'", filename)
                return
        self.files.append([filename, 0])
        self._update_table()
        log.debug("Item added: '%s'", filename)

    def _update_item(self, filename, progress):
        for item in self.files:
            if item[0] == filename:
                log.debug("Updating item '%s' progress to %i%%", filename, progress)
                item[1] = progress
        self._update_table()

    def _remove_item(self, filename):
        for item in self.files:
            if item[0] == filename:
                self.files.remove(item)
                log.debug("Item removed from list '%s'", filename)
        self._update_table()

    def _update_table(self):
        self.table.clearContents()
        self.table.setRowCount(len(self.files))
        for i, item in enumerate(self.files):
            filename, progress = (
                QtWidgets.QTableWidgetItem(item[0]),
                QtWidgets.QTableWidgetItem(str(item[1]) + "%"),
            )
            filename.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            progress.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            progress.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            self.table.setItem(i, 0, filename)
            self.table.setItem(i, 1, progress)

    def _delete_file(self):
        if self.table.item(self.table.currentRow(), 0) is None:
            return
        filename = self.table.item(self.table.currentRow(), 0).text()
        try:
            delete_file(filename)
        except PermissionError as error:
            QtWidgets.QMessageBox.critical(
                self,
                "File in use",
                "This file is being played or downloaded, so it can't be removed.",
            )
            log.debug("Failed to delete file '%s: '%s'", filename, error)
            return
        self._remove_item(filename)
        config.set("files", json.dumps(self.files))
        config.save()

    def _load_files(self):
        local_files = json.loads(config.get("files"))
        log.debug(local_files)
        self.files = local_files
        for file in self.files:
            if not os.path.isfile(file[0]):
                self.files.remove(file)

        self._next_file = get_next_filename()
        self._add_item(self._next_file)
        self.file_ready = download_file_async(self._next_file, self._update_item)
        config.set("files", json.dumps(self.files))
        config.save()

    def reload_files(self):
        download_directory = ""
        while download_directory == "":
            QtWidgets.QMessageBox.information(
                self,
                "Select Download Directory",
                "Please select the directory where you want video files to be saved.",
            )
            download_directory = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Select Download Directory",
                os.path.expanduser("~/Downloads"),
                QtWidgets.QFileDialog.ShowDirsOnly,
            )
        log.debug("Setting download directory to '%s'", download_directory)
        config.set("download_directory", download_directory)
        config.save()
        self._load_files()

    def get_next_filename(self):
        if self._next_file is None:
            raise AttributeError("Filename not loaded yet...")
        return self._next_file
