### Instalacion

Instalar dependencias.

```shell
pip install requeriments.txt
```

Correr el siguiente comando en la base de datos para crear una tarea programada que se encargue
de crear los ficheros logicos con las transacciones que han ocurrido.

```sybase
CREATE EVENT "DBA"."e_backup_incremental"
SCHEDULE "e_backup_db_1" START TIME '05:00' EVERY 1 MINUTES ON ( 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' ) START DATE '2010-05-03'
HANDLER
begin
    begin
  declare @db varchar(128);
  declare @backup_folder varchar(256);
  declare @database_folder varchar(256);
  select "db_name"(0) into @db from "dummy";
  
  set @backup_folder = 'D:\\salva_incremental\\' || @db;
  set @database_folder = 'D:\\' || @db;
  
  call "xp_cmdshell"('dbbackup.exe -n -y -r -t -c "uid=dba;pwd=sql;dbn=' || @db || ';eng= ' || @@servername || '" ' || @backup_folder,'no_output');
  
  call "xp_cmdshell"('forfiles /p ' || @backup_folder || ' /m *.LOG /d -2 /c "cmd /c del @path"','no_output');
  call "xp_cmdshell"('forfiles /p ' || @database_folder || ' /m *.LOG /c "cmd /c del @path"','no_output');
end
```

Correr aplicacion para restablecer logicos

```shell
python restore.py
```

Correr aplicacion para configurar los logicos de la base de datos

```shell
python log.py
```