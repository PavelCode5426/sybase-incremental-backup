### Instalacion

Instalar dependencias.

```shell
pip install requeriments.txt
```

Correr el siguiente comando en la base de datos para crear una tarea programada que se encargue
de crear los ficheros logicos con las transacciones que han ocurrido.

```sybase
CREATE EVENT "incremental_backup" ON SCHEDULE
START TIME '06:00' EVERY 10 MINUTE ON ( 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' ) START DATE '2023-09-01'
GO
declare
    @db varchar(128);
        @backup_folder
        varchar(256);
begin
    select "db_name"(0) into @db from "dummy";
    call "xp_cmdshell"('dbbackup.exe -c "uid=dba;pwd=sql;dbn=' || @db || ';eng= ' || @@servername || '" -o d:\\salva1\\' ||
                   @db || '_backup_log.txt -x -y d:\\salva1', 'no_output')
end;
        COMMENT
        ON EVENT "DBA"."{{database}}" IS 'Este evento garantiza hacer la salva incremental de la base de datos cada 10 minutos';
```

Correr aplicacion para restablecer logicos

```shell
python restore.py
```

Correr aplicacion para configurar los logicos de la base de datos

```shell
python log.py
```