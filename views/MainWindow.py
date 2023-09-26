import datetime
import os
from pathlib import Path
import glob

from PyQt6.QtWidgets import QMainWindow, QMessageBox, QPushButton, QLabel, QFileDialog, \
    QTableWidget, QTableWidgetItem, QCheckBox, QSpinBox, QLineEdit, QDialog
from PyQt6.uic import loadUi

from core.dbbackup import restoreDatabaseLogFile, restoreDatabaseLogsDirectory, clearDBBackup
from core.dblog import updateDBLogConfiguration, clearDBLogConfiguration, loadDBLogConfiguration
from core.models import DBLogConfig, DBBackupConfig
from views import CommonWindow

from views.RestoreDatabaseWindow import RestoreDatabaseWindow


class MainWindow(CommonWindow):
    log_version_label: QLabel
    starting_offset_label: QLabel
    truncation_offset_label: QLabel
    current_offset_label: QLabel
    timeline_guid_label: QLabel
    timeline_creation_time_label: QLabel
    log_guid_label: QLabel
    log_file_label: QLabel
    mirror_file_label: QLabel
    backup_folder_label: QLabel

    logs_table: QTableWidget
    activate_backup_checkbox: QCheckBox
    backup_minutes_interval_spinbox: QSpinBox
    db_connection_line_edit: QLineEdit

    log_file_button: QPushButton
    mirror_file_button: QPushButton
    save_config_button: QPushButton
    delete_config_button: QPushButton
    backup_folder_button: QPushButton

    file_restore_button: QPushButton
    directory_restore_button: QPushButton
    restore_selected_button: QPushButton

    _dblog_config: DBLogConfig
    _dbbackup_config: DBBackupConfig

    def __init__(self, dblog_config: DBLogConfig, dbbackup_config: DBBackupConfig) -> None:
        super(MainWindow, self).__init__()
        loadUi('ui/MainWindow.ui', self)

        self.save_config_button.clicked.connect(self.updateConfiguration)
        self.delete_config_button.clicked.connect(self.clearConfiguration)
        self.log_file_button.clicked.connect(self.selectLogFileHandler)
        self.mirror_file_button.clicked.connect(self.selectMirrorFileHandler)
        self.logs_table.itemSelectionChanged.connect(self.changeTableSelectionHandler)
        self.activate_backup_checkbox.toggled.connect(self.toggleCheckbox)
        self.file_restore_button.clicked.connect(self.restoreFile)
        self.directory_restore_button.clicked.connect(self.restoreDirectory)
        self.restore_selected_button.clicked.connect(self.restoreSelectedFiles)
        self.backup_folder_button.clicked.connect(self.selectBackupFolderHanlder)

        self._dblog_config = dblog_config
        self._dbbackup_config = dbbackup_config
        self.loadConfiguration()

    def loadConfiguration(self):
        self.log_version_label.setText(self._dblog_config.log_version)
        self.starting_offset_label.setText(self._dblog_config.starting_offset)
        self.truncation_offset_label.setText(self._dblog_config.truncation_offset)
        self.current_offset_label.setText(self._dblog_config.current_offset)
        self.timeline_guid_label.setText(self._dblog_config.timeline_guid)
        self.timeline_creation_time_label.setText(self._dblog_config.timeline_creation_time)
        self.log_guid_label.setText(self._dblog_config.log_guid)

        if self._dblog_config.log_file:
            self.log_file_label.setText(self._dblog_config.log_file.as_posix())
        if self._dblog_config.log_mirror_file:
            self.mirror_file_label.setText(self._dblog_config.log_mirror_file.as_posix())
        if self._dbbackup_config.backup_folder:
            self.backup_folder_label.setText(self._dbbackup_config.backup_folder.as_posix())

        self.activate_backup_checkbox.setChecked(self._dbbackup_config.active_backup)
        self.toggleCheckbox(self.activate_backup_checkbox.isChecked())

        self.db_connection_line_edit.setText(self._dbbackup_config.database_connection)
        self.backup_minutes_interval_spinbox.setValue(self._dbbackup_config.backup_minutes_interval)

        self.__fillTable()

    def selectLogFileHandler(self):
        file = self.__saveFileSelector('log', self.log_file_label.text())
        if file:
            self._dblog_config.log_file = Path(file)
            self.log_file_label.setText(file)

    def selectMirrorFileHandler(self):
        file = self.__saveFileSelector('mlog', self.mirror_file_label.text())
        if file:
            self._dblog_config.log_mirror_file = Path(file)
            self.mirror_file_label.setText(file)

    def selectBackupFolderHanlder(self):
        folder = self.__directorySelector()
        if folder:
            self._dbbackup_config.backup_folder = Path(folder)
            self._dbbackup_config.updateConfigurationFile()
            self.loadConfiguration()

    def changeTableSelectionHandler(self, *args, **kwargs):
        selectedItems = self.logs_table.selectedIndexes()
        self.restore_selected_button.setDisabled(not len(selectedItems))

    def toggleCheckbox(self, checked):
        disabled = not checked
        self.backup_minutes_interval_spinbox.setDisabled(disabled)
        self.db_connection_line_edit.setDisabled(disabled)
        self.backup_folder_button.setDisabled(disabled)

    def __saveFileSelector(self, suffix: str = '*', filename: str = ''):
        file, _ = QFileDialog.getSaveFileName(None, 'Seleccione el fichero', filename, f'Archivos (*.{suffix})')
        return file

    def __fileSelector(self, suffix: str = '*', filename: str = ''):
        file, _ = QFileDialog.getOpenFileName(None, 'Seleccione el fichero', filename, f'Archivos (*.{suffix})')
        return file

    def __directorySelector(self):
        directory = QFileDialog.getExistingDirectory(None, 'Seleccione el directorio')
        return directory

    def __fillTable(self):
        backup_folder = self._dbbackup_config.backup_folder
        if not backup_folder.exists():
            os.mkdir(backup_folder)
        files = self._dbbackup_config.backupFilesInBackupFolder()
        self.logs_table.setRowCount(len(files))

        for index, file in enumerate(files):
            self.logs_table.setItem(index, 0, QTableWidgetItem(file.name))
            modification_date = datetime.datetime.fromtimestamp(file.stat().st_ctime).strftime('%m/%d/%Y, %H:%M:%S')
            self.logs_table.setItem(index, 1, QTableWidgetItem(modification_date))
            size = round(file.stat().st_size / 125000, 2)
            self.logs_table.setItem(index, 2, QTableWidgetItem(f'{size} MB'))

    def __showTerminalOutput(self, output: str):
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setInformativeText(output)
        message_box.setWindowTitle("Salida del comando")
        message_box.exec()

    def restoreFile(self):
        file = Path(self._fileSelector('log'))
        if not file:
            return
        restoreDatabaseLogFile(self._dbbackup_config.database, file)

    def restoreDirectory(self):
        directory = Path(self._directorySelector())
        if not directory:
            return
        restoreDatabaseLogsDirectory(self._dbbackup_config.database, directory)

    def restoreSelectedFiles(self):
        files = self.logs_table.selectedIndexes()
        if not files:
            return

        rows = set([file.row() for file in files])

        for row in rows:
            file = self.logs_table.item(row, 0).text()
            file = self._dbbackup_config.backup_folder.joinpath(file)
            restoreDatabaseLogFile(self._dbbackup_config.database, file)

    def clearConfiguration(self):
        output = clearDBLogConfiguration(self._dblog_config)
        clearDBBackup(self._dbbackup_config)
        self._dblog_config.updateDblogParams(output)
        self._dbbackup_config.updateConfigurationFile()
        self.loadConfiguration()
        self._showTerminalOutput(output)

    def __isValidConfiguration(self) -> bool:
        valid = self.log_file_label.text() and self.mirror_file_label.text()
        if valid and self.activate_backup_checkbox.isChecked():
            valid = valid and self.db_connection_line_edit.text() and self.backup_folder_label.text()
        return valid

    def updateConfiguration(self):
        message = QMessageBox(self)
        if not self.__isValidConfiguration():
            message.setWindowTitle("Error en los datos de entrada")
            message.setInformativeText("Formulario invalido, revise la configuracion")
            message.setIcon(message.Icon.Information)
            return message.exec()

        message.setInformativeText("Aplicar configuracion?")
        message.setIcon(message.Icon.Question)
        message.setStandardButtons(message.StandardButton.Ok | message.StandardButton.Cancel)
        if message.exec() == message.StandardButton.Ok:
            self.updateDBLogConfiguration()
            self.updateDBBackupConfiguration()
            self.loadConfiguration()

    def updateDBLogConfiguration(self):
        output = updateDBLogConfiguration(self._dblog_config)
        self._showTerminalOutput(output)
        self._dblog_config = loadDBLogConfiguration(self._dblog_config.database)

    def updateDBBackupConfiguration(self):
        self._dbbackup_config.backup_minutes_interval = self.backup_minutes_interval_spinbox.value()
        self._dbbackup_config.active_backup = self.activate_backup_checkbox.isChecked()
        self._dbbackup_config.database_connection = self.db_connection_line_edit.text()
        self._dbbackup_config.updateConfigurationFile()
