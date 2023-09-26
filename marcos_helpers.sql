/*
 Mecanismo para implementar la SALVA INCREMENTAL en SYBASE:
2-
SALVA INCREMENTAL:
Pasos para modificar el mecanismo de salva actual de las BDs de SICSA y hacerlo más eficiente
BD: CEVA_LLB_HD

En EL SERVIDOR:

1-
Parar la BD.

2-
SHELL del DOS:
Setearle el mirror del lógico de la BD a un subdirectorio en otro servidor (Ej AerovarApp). Ello permite tener una copia del lógico en otro servidor.
Es aconsejable también tener la BD, el LÓGICO y el MIRROR en DISPOSITIVOS DIFERENTES!!!
NOTA: Mapear la torre X, Y y Z a dichos subdirectorios

AVMarcos:
	X => \\avaimee\DB_Backup
	Y => \\avaimee\DB_Log
	Z => \\avaimee\DB_Mlg
	
	
	dblog -t Y:\micargo.lombillo.log -m Z:\micargo.lombillo_mirror.mlg d:\sicsa\db_consolidada\micargo.lombillo.db
NOTA:
En nuestro caso probaremos a tener los 3 ficheros (.db, .log y .mlg) en el mismo servidor y después Piotr los copiará para otro a través de Tareas Programadas 
*/
	dblog -t d:\salva_log\micargo.lombillo.log -m d:\salva_mlg\micargo.lombillo_mirror.mlg d:\sicsa\db\micargo.lombillo\micargo.lombillo.db
	
/*
3-
Reiniciar la BD.
  3.1-
  Sybase Central: Levantar la BD a través de un servicio con los siguientes parámetros:
	-n micargo.lombillo_hd
	-x tcpip(port=11143)
	-ti 60
	"D:\sicsa\db\micargo.lombillo\micargo.lombillo.db"
	-n micargo.lombillo_hd  
	
  Si no se conecta por el servicio levantar la BD a traves de un acceso directo a dbsrv9.exe. 
  Sería:
*/	
	"C:\Program Files\Sybase\SQL Anywhere 9\win32\dbsrv9.exe" -x tcpip(port=11143) -ti 60 -n micargo.lombillo_hd "D:\Sicsa\DB\MiCargo.Lombillo\micargo.lombillo.db" -n micargo.lombillo_hd

/*
4-
Modificar el evento de salva de la BD para hacer FULL BACKUP
*/
if not exists(select * from sys.SYSEVENT where event_name = 'e_backup_db') then	
	CREATE EVENT "e_backup_db"
	SCHEDULE "e_backup_db_1" START TIME '06:00' EVERY 12 HOURS ON ( 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' ) START DATE '2018-11-13'
	HANDLER
	begin
	  declare @db char(20);
	  //Hacer FULL BACKUP de la BD
	  backup database directory 'D:\\Salva_FullBk\\';
	end;
	COMMENT ON EVENT "e_backup_db" IS 'Este evento garantiza hacer FULL BACKUP de la BD cada 12hr.';
end if;
		
/*
5-
Eliminar los anteriores eventos de salva de la BD
*/
if exists(select * from sys.SYSEVENT where event_name = 'e_backup1_db') then	
	DROP EVENT e_backup1_db;
end if;
if exists(select * from sys.SYSEVENT where event_name = 'e_backup2_db') then	
	DROP EVENT e_backup2_db;
end if;	
if exists(select * from sys.SYSEVENT where event_name = 'e_backup3_db') then	
	DROP EVENT e_backup3_db;
end if;
	
/*
En LA PC CLIENTE:
6-
SHELL del DOS:
NOOOOOOOOOO:
	Hacer full backup de la BD  (debe ser el mismo subdirectorio donde salvamos los mirrors del lógico en el punto anterior).
	NOTA: Ponerlo en una tarea programada que corra cada 12hr.
		PC Cliente: AVAimee
			dbbackup -c "enginename=CEVA_LLB_Consolidada;commlinks=TCPIP(HOST=192.168.126.37);uid=dba;pwd=sql" -y -q c:\DBBackup

		PC Cliente: AEROVARAPP
	dbbackup -c "enginename=micargo.lombillo;commlinks=TCPIP(HOST=192.168.126.24;PORT=11143);uid=dba;pwd=sql" -y -q d:\SalvaLog
/NOOOOOOOOOO

	Hacer BACKUP INCREMENTAL de la BD (El target_directory debe ser el subdirectorio donde salvamos los mirrors del lógico).
	NOTA: Ponerlo en una tarea programada que corra cada 10min.
		PC Cliente: AVAimee
*/		
		dbbackup -t -r -y -c "enginename=CEVA_LLB_Consolidada;commlinks=TCPIP(HOST=192.168.126.37);uid=dba;pwd=sql" c:\DB_Mlg

/*
		PC Cliente: AVMarcos1
*/		
		dbbackup -t -r -y -c "enginename=micargo.lombillo_hd;commlinks=TCPIP(HOST=192.168.126.35;PORT=11143);uid=dba;pwd=sql" d:\Salva_Mlg

/*
OJO:
En caso de que se corrompa la BD el mecanismo de actualización sería:
	- Aplicarle todos los lógicos salvados (salvas incrementales) a la última salva de la BD (fichero .db obtenido en el último FULL BACKUP)
		dbsrv9 sicsa_hav.db -a 151113AA.log
		dbsrv9 sicsa_hav.db -a 151113AB.log
		dbsrv9 sicsa_hav.db -a 151113AC.log
		...
		dbsrv9 sicsa_hav.db -a <ultimo fichero .log>
		
	Ej.	
		dbsrv9 d:\sicsa\db_consolidada\micargo.lombillo.db -a Y:\151127AB.log
		dbsrv9 d:\sicsa\db_consolidada\micargo.lombillo.db -a Y:\151127AC.log
		dbsrv9 d:\sicsa\db_consolidada\micargo.lombillo.db -a Y:\151127AD.log

Por tanto el mecanismo de restaura quedaría así:	
1- Hacer una salva del BK de la BD
2- Aplicar los lógicos incrementales a la BD
	NOTA: Los puntos 1 y 2 se automatizaron en el fichero de lotes D:\SICSA\DB\restore_db.bat que quedó de la siguiente manera.
	
    -----------D:\SICSA\DB\restore_db.bat-----------

echo off
setlocal
color 9f
echo.
set /p v_DBName=Teclee el nombre de la BD corrupta:
set /p v_DBPath=Teclee el camino de la BD corrupta:
set /p v_DBBkPath=Teclee el camino de la BD Backup:
set /p v_LogPath=Teclee el camino de los ficheros Logs a aplicar (salva incremental):
set /p v_MlgPath=Teclee el camino de los ficheros Mlg (mirrors del logico):

REM Validando el nombre de la BD dado por el usuario (quitándole la extensión si la tiene)
set v_DBName_ext=%v_DBName:~-3%
IF %v_DBName_ext%==.db set v_DBName=%v_DBName:.db=%

REM Obteniendo la fecha de la BD Backup en la variable "v_DBDate"
FORFILES /P %v_DBBkPath%\ /S /M %v_DBName%.db /c "cmd /c echo @fdate > %v_DBBkPath%\db_date.txt"
set /p v_DBDate=<%v_DBBkPath%\db_date.txt

REM Estableciendo una variable para almacenar la fecha del dia
set v_today=%date%

REM Eliminando el separador de fecha para nombrar el subdirectorio de copia para la BD BK
set v_DBDate_dir=%v_today:/=%
rem echo %v_DBName% %v_DBBkPath% %v_LogPath% %v_DBDate% %v_DBDate_dir%

REM Haciendo una copia de la BD Backup
XCOPY %v_DBBkPath%\%v_DBName%.* %v_DBBkPath%\%v_DBDate_dir%\ /I /F /Y

REM Visualizando los lógicos incrementales a aplicar a la BD Backup
rem FORFILES /P %v_LogPath%\ /S /M *.log /C "cmd /c echo @fname" /d +%v_DBDate%

REM Aplicando los lógicos incrementales a la BD Backup
FORFILES /P %v_LogPath%\ /S /M *.log /C "cmd /c dbeng9 %v_DBBkPath%\%v_DBName%.db -a @path -ga" /d +%v_DBDate%

REM Sobreescribiendo la BD corrupta con la actualizada
rem XCOPY %v_LogPath%\%v_DBName%.log %v_MlgPath%\%v_DBName%_mirror.mlg /I /F /Y
rem XCOPY %v_DBBkPath%\%v_DBName%.log %v_LogPath%\ /I /F /Y
XCOPY %v_DBBkPath%\%v_DBName%.db %v_DBPath%\ /I /F /Y

color

	-----------D:\SICSA\DB\restore_db.bat-----------
*/			
