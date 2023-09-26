import glob
from pathlib import Path
import configparser
import re
import os
from uuid import uuid1


class Config:
    database: Path = None

    def __init__(self, database: Path) -> None:
        self.database = database

    def _search_params(self, regular_expresion, lines):
        founded = re.findall(regular_expresion, lines)
        if founded:
            return founded[0]
        return None


class DBLogConfig(Config):
    def __init__(self, database: Path, dblog_output: str) -> None:
        super(DBLogConfig, self).__init__(database)
        self.updateDblogParams(dblog_output)

    def updateDblogParams(self, dblog_output: str):
        lines = dblog_output.replace("\r", "")
        self.log_version = self._search_params(r'Version (\d+\.\d+\.\d+\.\d+)', lines)
        self.starting_offset = self._search_params(r'starting offset is (\d+)', lines)
        self.truncation_offset = self._search_params(r'truncation offset is (\d+)', lines)
        self.current_offset = self._search_params(r'relative offset is (\d+)', lines)
        self.timeline_guid = self._search_params(r'Current timeline GUID: (.+)', lines)
        self.timeline_creation_time = self._search_params(r'Current timeline UTC creation time: (.+)', lines)
        self.log_guid = self._search_params(r'Current transaction log GUID: (.+)', lines)

        file = self._search_params(r'log file "([^"]+)', lines)
        self.log_file = Path(file) if file else None
        file = self._search_params(r'log mirror file "([^"]+)', lines)
        self.log_mirror_file = Path(file) if file else None

    def allLogFiles(self) -> [Path]:
        files = []
        if self.log_file:
            directory = self.log_file.parent
            suffix = self.log_file.suffix

            for root, subfolders, _files in os.walk(directory):
                for file in _files:
                    if file.endswith(suffix):
                        files.append(Path(os.path.join(root, file)))
        return files


class DBBackupConfig(Config):
    __config_suffix = '.ini'
    __config_section = 'default'

    service_name: str
    database_connection: str
    active_backup: bool
    backup_minutes_interval: int
    backup_folder: Path

    def __init__(self, database: Path) -> None:
        super(DBBackupConfig, self).__init__(database)
        self.__parser = configparser.ConfigParser()
        self.__loadConfiguration(database)

    def __writeConfigFile(self):
        with open(self.config_file, 'w') as file:
            self.__parser.write(file)

    def __loadConfiguration(self, database: Path):
        filename, suffix = os.path.splitext(database)
        self.config_file = Path(f'{filename}{self.__config_suffix}')

        if not self.config_file.exists():
            self.__parser.add_section(self.__config_section)
            self.__parser.set(self.__config_section, 'service_name', f'DBBackup_{uuid1()}_{database.name}')
            self.__parser.set(self.__config_section, 'active_backup', 'True')
            self.__parser.set(self.__config_section, 'database', database.__str__())
            self.__parser.set(self.__config_section, 'backup_minutes_interval', '10')
            self.__parser.set(self.__config_section, 'backup_folder', '')
            self.__parser.set(self.__config_section, 'database_connection', '')
            self.__writeConfigFile()

        self.__parser.read(self.config_file)
        self.service_name = self.__parser.get(self.__config_section, 'service_name')
        self.active_backup = self.__parser.getboolean(self.__config_section, 'active_backup')
        self.backup_minutes_interval = self.__parser.getint(self.__config_section, 'backup_minutes_interval')
        self.backup_folder = Path(self.__parser.get(self.__config_section, 'backup_folder'))
        self.database_connection = self.__parser.get(self.__config_section, 'database_connection')

    def updateConfigurationFile(self):
        self.__parser.set(self.__config_section, 'service_name', self.service_name)
        self.__parser.set(self.__config_section, 'database', self.database.__str__())
        self.__parser.set(self.__config_section, 'active_backup', str(self.active_backup))
        self.__parser.set(self.__config_section, 'backup_minutes_interval', str(self.backup_minutes_interval))
        self.__parser.set(self.__config_section, 'backup_folder', str(self.backup_folder))
        self.__parser.set(self.__config_section, 'database_connection', self.database_connection)
        self.__writeConfigFile()

    def backupFilesInBackupFolder(self):
        # files = self.backup_folder.glob('/*.log')
        files = glob.glob(f'{self.backup_folder}/*.log')
        return [Path(file) for file in files]
