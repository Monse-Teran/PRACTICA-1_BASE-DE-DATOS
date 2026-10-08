\# Reporte de Levantamiento Local - Sistema de Visualización de Datos Sísmicos



\## 1. Requisitos Previos

\* \*\*Sistema operativo:\*\* Windows / Terminal (CMD).

\* \*\*Herramientas de contenedores:\*\* Docker Desktop instalado y en ejecución.

\* \*\*Control de versiones:\*\* Git y GitHub.



\---



\## 2. Pasos de Ejecución (En orden de ejecución)

1\. \*\*Fork y Clonación:\*\* Se realizó un \*fork\* del repositorio original y se clonó de forma local en el equipo mediante el comando `git clone`.

2\. \*\*Construcción y Arranque de Contenedores:\*\* 

&#x20;  \* Se aseguró que Docker Desktop estuviera activo.

&#x20;  \* Se ejecutó el comando para levantar el entorno multi-contenedor:

&#x20;    ```cmd

&#x20;    docker-compose up -d

&#x20;    ```

3\. \*\*Conexión a la Base de Datos PostgreSQL:\*\*

&#x20;  \*\*Se intento entrar a una base de datos incorrecta pues no sabia con exactitud cual era la correcta\*\*

&#x20;  \* Se accedió al contenedor de la base de datos para verificar las instancias disponibles con el comando `\\l`.

&#x20;  \* Se identificó y seleccionó la base de datos correcta (`datawarehouse`) usando `\\c datawarehouse`.

4\. \*\*Verificación de Tablas y Consultas SQL:\*\*

&#x20;  \* Se listaron las relaciones con `\\dt`, confirmando la existencia de las tablas (`dim\_sismos`, `dim\_zonas`, etc.).

&#x20;  \* Se ejecutaron consultas de prueba en las tablas principales para comprobar el funcionamiento correcto del almacenamiento de datos.

5\. \*\*Documentación y Registro:\*\*

&#x20;  \* Se actualizó el archivo `README.md` añadiendo la dirección del fork y el identificador de la confirmación (\*commit\*).

&#x20;  \* Se subieron los cambios al repositorio remoto mediante `git push`.



\---



\## 3. Errores Encontrados y Soluciones



\* \*\*Error de conexión inicial a la base de datos:\*\*

&#x20; \* \*\*Problema:\*\* Al intentar conectarse directamente con `docker exec -it ... psql -U postgres -d seismic\_db`, la terminal arrojó el error: `database "seismic\_db" does not exist`.

&#x20; \* \*\*Solución:\*\* Se ingresó primero a PostgreSQL sin especificar la base de datos (`docker exec -it ... psql -U postgres`), se ejecutó el comando `\\l` para listar los nombres reales disponibles, detectando que la base de datos del proyecto se llamaba `datawarehouse`. Posteriormente, se cambió de base de datos con el comando interno `\\c datawarehouse`, resolviendo el acceso con éxito.



\---



\## 4. Evidencias



\### Arranque de contenedores en Docker

\*(La imagen de esta evidencia se encuentra en la parte de evidencias/"contenedores")\*



\### Aplicación y servicios corriendo en el equipo

\*(La imagen de esta evidencia se encuentra en el apartado evidencias/ "aplicacion y servicios corriendo en el equipo")\*



\### Resultados de las consultas en la base de datos

\*(La imagen de esta evidencia se encunetra en el apartado de evidencias/se muestran las consultas a "dim\_sismos" y "dim\_zonas" con sus respectivos resultados en tabla)\*

