import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QFileDialog

from views.RestoreDatabaseWindow import RestoreDatabaseWindow


def init_restore_app():
    app = QApplication(sys.argv)
    file, _ = QFileDialog.getOpenFileName(None, 'Seleccione la base de datos', None, 'Archivos (*.db)')
    if not file:
        return

    file = Path(file)
    main = RestoreDatabaseWindow(file)
    main.show()
    sys.exit(app.exec())


init_restore_app()
