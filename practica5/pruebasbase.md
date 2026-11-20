
## Prueba 1: Estado Inicial (Inserción de Datos de Prueba)

En esta primera etapa se registran los datos base en la copia de la base de datos (`postgres_ej26`) para verificar la relación 1:N entre un autor y sus libros publicados antes de aplicar cualquier borrado.

* **Operaciones ejecutadas:**
  ```sql
  INSERT INTO autores (autor_id, biografia)
  VALUES (701, 'Autor de ciencia ficción y narrativa especulativa');

  INSERT INTO libros (libro_id, titulo, anio_publicacion, autor_id)
  VALUES
      (801, 'Crónicas del Horizonte', 2021, 701),
      (802, 'Ecos en la Órbita', 2024, 701);
  ```
* **Resultado observado:**
  * En `autores` existe el registro con `autor_id = 701`.
  * En `libros` existen dos registros hijos (`libro_id = 801` y `libro_id = 802`) vinculados a `autor_id = 701`.


<img width="1531" height="582" alt="image" src="https://github.com/user-attachments/assets/09a4e003-af62-4c63-b0e0-0e4fba93931a" />

## Prueba 2: Comportamiento con `ON DELETE RESTRICT` (Restricción Original)

Se intenta eliminar el renglón padre (`autor_id = 701`) mientras mantiene registros dependientes en la tabla `libros`, conservando la regla referencial original `ON DELETE RESTRICT`.

* **Operación ejecutada:**
  ```sql
  DELETE FROM autores WHERE autor_id = 701;
  ```
* **Resultado observado:**
  * PostgreSQL bloquea la eliminación y devuelve un error de violación de integridad referencial (`ERROR: update or delete on table "autores" violates foreign key constraint "fk_libros_autor" on table "libros"`).
* **Análisis de impacto:**
  * **Qué se pierde:** Ningún registro; la operación es rechazada por el motor de base de datos.
  * **Qué se conserva:** Se mantienen intactos el autor `701`, sus dos libros (`801` y `802`), y el resto de las tablas del sistema (`comics`, `usuarios`, `playlist`, `produccion_audiovisual`, `resenas`, `visualiza` y `esta_basada_en`).


<img width="1418" height="134" alt="image" src="https://github.com/user-attachments/assets/ea7b3ddf-9682-4426-a556-fd23a7a7f8fa" />

## Prueba 3: Cambio a `ON DELETE CASCADE` y Borrado del Renglón Padre

Se modifica la restricción `fk_libros_autor` en la base de prueba `postgres_ej26` cambiando su acción referencial de `RESTRICT` a `CASCADE`, y se vuelve a ejecutar la eliminación del renglón padre.

* **Operaciones ejecutadas:**
  ```sql
  ALTER TABLE libros
      DROP CONSTRAINT fk_libros_autor,
      ADD CONSTRAINT fk_libros_autor
          FOREIGN KEY (autor_id) REFERENCES autores (autor_id)
          ON DELETE CASCADE
          ON UPDATE CASCADE;

  DELETE FROM autores WHERE autor_id = 701;
  ```
* **Resultado observado:**
  * PostgreSQL ejecuta la eliminación exitosamente (`DELETE 1`) y propaga el borrado hacia la tabla hija. Al consultar ambas tablas para `autor_id = 701`, ambas devuelven `0 rows`.
* **Análisis de impacto:**
  * **Qué se pierde:** Se elimina el registro padre en `autores` (`autor_id = 701`) y se pierden automáticamente todos sus renglones hijos en `libros` (`libro_id = 801` y `libro_id = 802`).
  * **Qué se conserva:** Se conservan los libros pertenecientes a otros autores, así como los registros independientes en `comics`, `usuarios`, `playlist`, `produccion_audiovisual`, `resenas` y `visualiza`.


<img width="690" height="353" alt="image" src="https://github.com/user-attachments/assets/d3d6b61b-cd8d-476e-a513-6c81add8ff3d" />
