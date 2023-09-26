from PyQt6.QtWidgets import QFileDialog, QMessageBox, QMainWindow


class CommonWindow(QMainWindow):
    def loadConfiguration(self):
        pass

    def _saveFileSelector(self, suffix: str = '*', filename: str = ''):
        file, _ = QFileDialog.getSaveFileName(None, 'Seleccione el fichero', filename, f'Archivos (*.{suffix})')
        return file

    def _fileSelector(self, suffix: str = '*', filename: str = ''):
        file, _ = QFileDialog.getOpenFileName(None, 'Seleccione el fichero', filename, f'Archivos (*.{suffix})')
        return file

    def _directorySelector(self):
        directory = QFileDialog.getExistingDirectory(None, 'Seleccione el directorio')
        return directory

    def _showTerminalOutput(self, output: str):
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setInformativeText(output)
        message_box.setWindowTitle("Salida del comando")
        message_box.exec()
