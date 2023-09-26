import datetime
import os
from glob import glob
from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QMessageBox, QPushButton, QFileDialog, \
    QTableWidget, QTableWidgetItem, QLabel
from PyQt6.uic import loadUi

from core.dbbackup import restoreDatabaseLogFile, restoreDatabaseLogsDirectory
from views import CommonWindow


class RestoreDatabaseWindow(CommonWindow):
    _database: Path
    _backup_folder: Path
    logs_table: QTableWidget

    backup_folder_label: QLabel
    backup_folder_button: QPushButton

    file_restore_button: QPushButton
    directory_restore_button: QPushButton
    restore_selected_button: QPushButton

    def __init__(self, database: Path) -> None:
        super(RestoreDatabaseWindow, self).__init__()
        loadUi('ui/RestoreDatabaseWindow.ui', self)
        self._database = database

        self.logs_table.itemSelectionChanged.connect(self.changeTableSelectionHandler)
        self.file_restore_button.clicked.connect(self.restoreFile)
        self.directory_restore_button.clicked.connect(self.restoreDirectory)
        self.restore_selected_button.clicked.connect(self.restoreSelectedFiles)
        self.backup_folder_button.clicked.connect(self.selectBackupFolderHanlder)

    def changeTableSelectionHandler(self, *args, **kwargs):
        selectedItems = self.logs_table.selectedIndexes()
        self.restore_selected_button.setDisabled(not len(selectedItems))

    def selectBackupFolderHanlder(self):
        folder = self._directorySelector()
        if folder:
            self._backup_folder = Path(folder)
            self.backup_folder_label.setText(folder)
            self.__fillTable()

    def __fillTable(self):
        backup_folder = self._backup_folder
        files = [Path(file) for file in backup_folder.glob('*.log')]
        self.logs_table.setRowCount(len(files))

        for index, file in enumerate(files):
            self.logs_table.setItem(index, 0, QTableWidgetItem(file.name))
            modification_date = datetime.datetime.fromtimestamp(file.stat().st_ctime).strftime('%m/%d/%Y, %H:%M:%S')
            self.logs_table.setItem(index, 1, QTableWidgetItem(modification_date))
            size = round(file.stat().st_size / 125000, 2)
            self.logs_table.setItem(index, 2, QTableWidgetItem(f'{size} MB'))

    def restoreFile(self):
        file = Path(self._fileSelector('log'))
        if not file:
            return
        restoreDatabaseLogFile(self._database, file)

    def restoreDirectory(self):
        directory = Path(self._directorySelector())
        if not directory:
            return
        restoreDatabaseLogsDirectory(self._database, directory)

    def restoreSelectedFiles(self):
        files = self.logs_table.selectedIndexes()
        if not files:
            return

        rows = set([file.row() for file in files])

        for row in rows:
            file = self.logs_table.item(row, 0).text()
            file = self._backup_folder.joinpath(file)
            restoreDatabaseLogFile(self._database, file)
