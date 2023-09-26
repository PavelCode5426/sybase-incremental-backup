from cx_Freeze import Executable, setup

files = ['ui']

exe_log_app = Executable(script='log.py', base='Win32GUI')
exe_restore_app = Executable(script='restore.py', base='Win32GUI')

setup(
    name="DBLogTools",
    version='1.0',
    description="Sybase dblog utils",
    author='PavelCode',
    executables=[exe_log_app, exe_restore_app],
    options={
        'build_exe': {'include_files': files}
    }
)
