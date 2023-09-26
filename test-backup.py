# 1- Cargar configuracion
# 2- Configurar la salva
# 3- Correrla indefinidamente
import os
from pathlib import Path
import argparse

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

if dbbackup_config.active_backup:
    if not dbbackup_config.backup_folder.exists():
        os.mkdir(dbbackup_config.backup_folder)
    if dbbackup_config.active_backup:
        output = runIncrementalBackup(dbbackup_config)
        logger.info(output)
