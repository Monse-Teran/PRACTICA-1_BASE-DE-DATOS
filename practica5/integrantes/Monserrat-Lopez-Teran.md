# Práctica 5 — Ejercicio 2.6

**Lopez Teran Monserrat** 

## Prueba individual de acciones referenciales

### 1. Relación seleccionada

Se elige la relación entre las tablas `libros` (padre) y `esta_basada_en` (hija).

La llave foránea `fk_basada_libro` relaciona `esta_basada_en.libro_id` con `libros.libro_id`.

La configuración original en la base de datos (`practica3_db`) era:

```sql
ON UPDATE CASCADE
ON DELETE RESTRICT
```

### 2. Prueba con `ON DELETE RESTRICT`

En una copia de la base de datos (`practica3_db_copia`), se crearon los registros temporales necesarios con identificador `9002` (un autor, un libro, una producción audiovisual y su vínculo de adaptación en `esta_basada_en`).

```sql
INSERT INTO autores (autor_id, biografia) 
VALUES (9002, 'Autor temporal de prueba');

INSERT INTO libros (libro_id, titulo, anio_publicacion, autor_id) 
VALUES (9002, 'Libro Temporal de Prueba', 2020, 9002);

INSERT INTO produccion_audiovisual (contenido_id, titulo, anio_estreno, tipo_produccion) 
VALUES (9002, 'Adaptacion Temporal', 2024, 'pelicula');

INSERT INTO esta_basada_en (contenido_id, libro_id, comic_id) 
VALUES (9002, 9002, NULL);
```

Posteriormente se intentó eliminar el libro padre:

```sql
DELETE FROM libros WHERE libro_id = 9002;
```

**Resultado:** PostgreSQL rechazó la operación porque el libro todavía estaba referenciado por un registro de adaptación en la tabla `esta_basada_en`. Tanto el libro como la relación de adaptación se conservaron intactos.

**Mensaje obtenido:**

```text
ERROR:  update or delete on table "libros" violates foreign key constraint "fk_basada_libro" on table "esta_basada_en"
DETAIL:  Key (libro_id)=(9002) is still referenced from table "esta_basada_en".
```

![alt text](<Evidencia1-ejercicio 2.6.png>)

### 3. Prueba con `ON DELETE CASCADE`

En la misma copia de la base de datos (`practica3_db_copia`) se modificó la llave foránea `fk_basada_libro` para cambiar su comportamiento de borrado a `CASCADE`:

```sql
ALTER TABLE esta_basada_en 
DROP CONSTRAINT fk_basada_libro;

ALTER TABLE esta_basada_en 
ADD CONSTRAINT fk_basada_libro 
FOREIGN KEY (libro_id) REFERENCES libros(libro_id) 
ON UPDATE CASCADE 
ON DELETE CASCADE;
```

Posteriormente se volvió a ejecutar la eliminación del libro padre:

```sql
DELETE FROM libros WHERE libro_id = 9002;
```

**Resultado:** PostgreSQL permitió eliminar el libro (`DELETE 1`) y eliminó automáticamente el registro de adaptación asociado en `esta_basada_en`, mientras que el autor (`autor_id = 9002`) y la producción audiovisual (`contenido_id = 9002`) se conservaron en sus respectivas tablas.

```sql
SELECT COUNT(*) AS libros_restantes FROM libros WHERE libro_id = 9002;
SELECT COUNT(*) AS adaptaciones_restantes FROM esta_basada_en WHERE libro_id = 9002;
```

La comprobación posterior mostró `0` registros tanto en `libros` como en `esta_basada_en` para el identificador `9002`.

![alt text](<Evidencia2-ejercicio 2.6.png>)

### 4. Comparación de resultados

| Acción | Qué sucede al eliminar un libro (`libros`) | Qué se conserva y qué se pierde |
| :--- | :--- | :--- |
| `RESTRICT` | Impide la eliminación si el libro está referenciado como obra de origen en `esta_basada_en`. | **Se conserva** tanto el libro como su relación de adaptación con la producción audiovisual. No se pierde ningún dato. |
| `CASCADE` | Elimina el libro y también elimina automáticamente sus registros vinculados en `esta_basada_en`. | **Se pierde** el libro y el vínculo histórico que indicaba en qué obra literaria estaba basada la producción. **Se conservan** el autor y la producción audiovisual. |

### 5. Acción correcta para el dominio

Para el proyecto de plataforma de streaming, la acción más adecuada es **`ON DELETE RESTRICT`**. Las producciones audiovisuales que son adaptaciones literarias requieren conservar la trazabilidad de la obra original en la que se basan (`esta_basada_en`). Eliminar un libro del catálogo no debería borrar automáticamente los registros de adaptación de películas o series existentes; si realmente se requiere dar de baja un libro, primero debe revisarse y actualizarse manualmente el registro de adaptación correspondiente.

### 6. Conclusión

La prueba permitió comprobar de manera práctica la diferencia entre `ON DELETE RESTRICT` y `ON DELETE CASCADE` sobre la relación `libros` → `esta_basada_en`. Se verificó que `RESTRICT` protege la integridad referencial e histórica del catálogo evitando borrados en cadena no deseados, mientras que `CASCADE` automatiza la eliminación de registros dependientes a costa de perder el vínculo de origen literario de las producciones.
