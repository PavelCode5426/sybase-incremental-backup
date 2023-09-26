from pathlib import Path

from PyQt6.QtWidgets import QMessageBox, QPushButton, QLabel
from PyQt6.uic import loadUi

from core.dblog import updateDBLogConfiguration, clearDBLogConfiguration, loadDBLogConfiguration
from core.models import DBLogConfig
from views import CommonWindow


class LogConfigurationWindow(CommonWindow):
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

    log_file_button: QPushButton
    mirror_file_button: QPushButton
    save_config_button: QPushButton
    delete_config_button: QPushButton
    _dblog_config: DBLogConfig

    def __init__(self, dblog_config: DBLogConfig) -> None:
        super(LogConfigurationWindow, self).__init__()
        loadUi('ui/LogConfigurationWindow.ui', self)

        self.save_config_button.clicked.connect(self.updateConfiguration)
        self.delete_config_button.clicked.connect(self.clearConfiguration)
        self.log_file_button.clicked.connect(self.selectLogFileHandler)
        self.mirror_file_button.clicked.connect(self.selectMirrorFileHandler)

        self._dblog_config = dblog_config
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

    def selectLogFileHandler(self):
        file = self._saveFileSelector('log', self.log_file_label.text())
        if file:
            self._dblog_config.log_file = Path(file)
            self.log_file_label.setText(file)

    def selectMirrorFileHandler(self):
        file = self._saveFileSelector('mlog', self.mirror_file_label.text())
        if file:
            self._dblog_config.log_mirror_file = Path(file)
            self.mirror_file_label.setText(file)

    def clearConfiguration(self):
        output = clearDBLogConfiguration(self._dblog_config)
        self._dblog_config.updateDblogParams(output)
        self.loadConfiguration()
        self._showTerminalOutput(output)

    def __isValidConfiguration(self) -> bool:
        valid = self.log_file_label.text() and self.mirror_file_label.text()
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
            self.loadConfiguration()

    def updateDBLogConfiguration(self):
        output = updateDBLogConfiguration(self._dblog_config)
        self._showTerminalOutput(output)
        self._dblog_config = loadDBLogConfiguration(self._dblog_config.database)
