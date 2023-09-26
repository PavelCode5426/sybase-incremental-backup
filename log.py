import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QFileDialog

from core.dblog import loadDBLogConfiguration
from views.LogConfigurationWindow import LogConfigurationWindow


def init_log_app():
    app = QApplication(sys.argv)
    file, _ = QFileDialog.getOpenFileName(None, 'Seleccione la base de datos', None, 'Archivos (*.db)')
    if not file:
        return

    file = Path(file)
    log_params = loadDBLogConfiguration(file)
    main = LogConfigurationWindow(log_params)
    main.show()
    sys.exit(app.exec())


init_log_app()
