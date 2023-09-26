# 1- Cargar configuracion
# 2- Configurar la salva
# 3- Correrla indefinidamente
import os
from pathlib import Path
from time import sleep
import schedule
import argparse

from core import logs
from core.dbbackup import runIncrementalBackup
from core.dblog import loadDBLogConfiguration
from core.logs import logger
from core.models import DBBackupConfig

parser = argparse.ArgumentParser()
parser.add_argument('database', type=str, help='Database path')
args = parser.parse_args()

database = Path(args.database)
dbbackup_config = DBBackupConfig(database)
dblog_config = loadDBLogConfiguration(database)


def execute_scheduler():
    if not dbbackup_config.active_backup:
        return
    if not dbbackup_config.backup_folder.exists():
        os.mkdir(dbbackup_config.backup_folder)
    output = runIncrementalBackup(dbbackup_config)
    logger.info(output)


schedule.every(dbbackup_config.backup_minutes_interval).minutes.do(execute_scheduler)

while True:
    schedule.run_pending()
    sleep(5)
