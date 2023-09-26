import subprocess
from pathlib import Path

from core.models import DBLogConfig


def showDatabaseServerHelp():
    subprocess.check_output(['dbsrv17', '-n'], shell=True)


def loadDBLogConfiguration(database: Path):
    file_path = database.as_posix()
    process = subprocess.check_output(['dblog', file_path], shell=True)
    output = process.decode('utf-8')
    return DBLogConfig(database, output)


def updateDBLogConfiguration(config: DBLogConfig):
    promp = ['dblog']

    promp.append('-t')
    promp.append(config.log_file)
    if config.log_mirror_file:
        promp.append('-m')
        promp.append(config.log_mirror_file)

    promp.append(config.database)
    process = subprocess.check_output(promp, shell=True)
    output = process.decode('utf-8')
    return output


def clearDBLogConfiguration(config: DBLogConfig):
    promp = ['dblog', '-n', '-il', '-is']
    promp.append(config.database)
    process = subprocess.check_output(promp, shell=True)
    output = process.decode('utf-8')
    return output


def restoreDBLogConfiguration(database: Path, log: Path):
    promp = ['dbsrv17', '-a', log]
    promp.append(database)
    process = subprocess.check_output(promp, shell=True)
    output = process.decode('utf-8')
    return output
