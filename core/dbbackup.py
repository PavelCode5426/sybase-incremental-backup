import subprocess
from pathlib import Path

from core import scheduler
from core.models import DBBackupConfig


# REQUIRE LA BASE DE DATOS APAGADA
def restoreDatabaseLogFile(database: Path, log_file: Path):
    promp = ['dbsrv17', database.as_posix(), '-a', log_file.as_posix()]
    process = subprocess.check_output(promp, shell=True)
    output = process.decode('utf-8')
    return output


# REQUIRE LA BASE DE DATOS APAGADA
def restoreDatabaseLogsDirectory(database: Path, directory: Path):
    promp = ['dbsrv17', database.as_posix(), '-ad', directory.as_posix()]
    process = subprocess.check_output(promp, shell=True)
    output = process.decode('utf-8')
    return output


def clearDBBackup(config: DBBackupConfig):
    config.active_backup = False


# NO FUNCIONA
def registerDBBackupAsScheduledTask(config: DBBackupConfig):
    script_path = Path('../backup.py')
    scheduler.createWindowTask(config.service_name, script_path)


# NO FUNCIONA
def removeDBBackupAsScheduledTask(config: DBBackupConfig):
    scheduler.removeWindowTask(config.service_name)


def runIncrementalBackup(config: DBBackupConfig):
    # dbbackup -y -t -r -c {conexion} {carpeta}
    promp = ['dbbackup', '-y', '-t', '-r', '-c']
    promp.append(config.database_connection)
    promp.append(config.backup_folder.as_posix())
    process = subprocess.check_output(promp, shell=True)
    output = process.decode('utf-8')
    return output
