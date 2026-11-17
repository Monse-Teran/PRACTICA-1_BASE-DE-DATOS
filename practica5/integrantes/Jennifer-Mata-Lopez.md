# Práctica 5 — Ejercicio 2.6
**Integrante:** Jennifer Mata López

## Prueba individual de acciones referenciales

### 1. Relación seleccionada

Se eligió la relación entre las tablas `autores` y `libros`.

La llave foránea `fk_libros_autor` relaciona `libros.autor_id` con `autores.autor_id`.

La configuración original era:

```sql
ON UPDATE CASCADE
ON DELETE RESTRICT
```

### 2. Prueba con ON DELETE RESTRICT

Se creó un autor temporal con identificador 9001 y un libro relacionado.

Se intentó eliminar al autor:

```sql
DELETE FROM autores
WHERE autor_id = 9001;
```

**Resultado:** PostgreSQL rechazó la operación porque el autor todavía estaba relacionado con un registro de la tabla `libros`.

Mensaje obtenido:

```text
ERROR: update or delete on table "autores" violates foreign key constraint "fk_libros_autor" on table "libros"
DETAIL: Key (autor_id)=(9001) is still referenced from table "libros".
```

### 3. Prueba con ON DELETE CASCADE

En una copia de la base de datos se modificó la llave foránea:

```sql
ALTER TABLE libros
DROP CONSTRAINT fk_libros_autor;

ALTER TABLE libros
ADD CONSTRAINT fk_libros_autor
FOREIGN KEY (autor_id)
REFERENCES autores(autor_id)
ON UPDATE CASCADE
ON DELETE CASCADE;
```

Posteriormente se eliminó el autor:

```sql
DELETE FROM autores
WHERE autor_id = 9001;
```

**Resultado:** PostgreSQL permitió eliminar al autor y eliminó automáticamente el libro relacionado.

La comprobación posterior mostró cero registros tanto en `autores` como en `libros` para el identificador utilizado.

### 4. Comparación de resultados

| Acción | Qué sucede al eliminar un autor |
|---|---|
| RESTRICT | Impide la eliminación si tiene libros relacionados. |
| CASCADE | Elimina al autor y también sus libros relacionados. |

### 5. Acción correcta para el dominio

Para el proyecto Club de Cine, la acción más adecuada es `ON DELETE RESTRICT`, porque los libros forman parte del catálogo y deben conservar su relación con los autores. Eliminar un autor no debería provocar la eliminación automática de sus libros.

### 6. Conclusión

La prueba permitió observar la diferencia entre las acciones referenciales RESTRICT y CASCADE. Se comprobó que RESTRICT protege los registros relacionados, mientras que CASCADE propaga la eliminación a las tablas dependientes.

Las pruebas se realizaron en una copia de la base de datos para evitar modificar el esquema original.