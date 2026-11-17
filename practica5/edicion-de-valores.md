# Práctica 5. Edición de valores

## 2.4 DML y transacciones

### 1. INSERT que toma valores de una consulta

Se utilizó una instrucción INSERT junto con SELECT para insertar
información en la tabla usuario_estandar a partir de los datos
existentes en la tabla usuarios.

```sql
INSERT INTO usuario_estandar
    (usuario_id, tipo_usuario, limite_resenas)
SELECT usuario_id, tipo_usuario, 0
FROM usuarios
WHERE usuario_id = 1
  AND tipo_usuario = 'estandar'
RETURNING *;

### 2. INSERT que resuelve conflictos cuando el registro ya existe

Se utilizó la cláusula ON CONFLICT para evitar insertar un registro
duplicado en la tabla usuario_estandar.

```sql
INSERT INTO usuario_estandar
    (usuario_id, tipo_usuario, limite_resenas)
SELECT usuario_id, tipo_usuario, 0
FROM usuarios
WHERE usuario_id = 1
  AND tipo_usuario = 'estandar'
ON CONFLICT (usuario_id) DO NOTHING
RETURNING *;

### 3. UPDATE dependiente de otra tabla

Se actualizó el límite de reseñas de un usuario estándar utilizando
una condición que consulta la tabla usuarios.

```sql
UPDATE usuario_estandar ue
SET limite_resenas = 5
WHERE EXISTS (
    SELECT 1
    FROM usuarios u
    WHERE u.usuario_id = ue.usuario_id
      AND u.tipo_usuario = 'estandar'
      AND u.fecha_registro = CURRENT_DATE
)
RETURNING *;

### 3. UPDATE dependiente de otra tabla

Se actualizó el límite de reseñas de un usuario estándar utilizando
una condición que consulta la tabla usuarios.

```sql
UPDATE usuario_estandar ue
SET limite_resenas = 5
WHERE EXISTS (
    SELECT 1
    FROM usuarios u
    WHERE u.usuario_id = ue.usuario_id
      AND u.tipo_usuario = 'estandar'
      AND u.fecha_registro = CURRENT_DATE
)
RETURNING *;

### 4. UPDATE utilizando CASE

Se utilizó CASE para modificar el valor de publicidad dependiendo
del límite de reseñas asignado al usuario.

```sql
UPDATE usuario_estandar
SET publicidad = CASE
    WHEN limite_resenas >= 5 THEN FALSE
    ELSE TRUE
END
RETURNING *;

### 2.4.3 DELETE con subconsulta y borrado lógico

**Borrado físico mediante subconsulta**

Se realizó una prueba utilizando un usuario temporal dentro de una transacción:

```sql
BEGIN;

INSERT INTO usuarios (usuario_id, correo, nombre, apellidos, tipo_usuario)
VALUES (999999, 'prueba_borrado@ejemplo.com', 'Usuario', 'Temporal', 'estandar');

INSERT INTO usuario_estandar (usuario_id, tipo_usuario, limite_resenas)
VALUES (999999, 'estandar', 0);

DELETE FROM usuarios
WHERE usuario_id IN (
    SELECT usuario_id
    FROM usuarios
    WHERE correo = 'prueba_borrado@ejemplo.com'
)
RETURNING usuario_id, correo;

ROLLBACK;
```

**Resultado:** PostgreSQL mostró `DELETE 1`, indicando que se eliminó un registro dentro de la transacción. Finalmente, `ROLLBACK` canceló los cambios y evitó que la eliminación fuera permanente.

**Efectos del borrado físico:** El registro se elimina de la tabla. En este esquema, algunas relaciones tienen `ON DELETE CASCADE`, por lo que también pueden eliminarse los registros relacionados con ese usuario.

**Borrado lógico**

El esquema actual no cuenta con una columna que indique si un usuario está activo o eliminado. Por ello, no es posible implementar directamente el borrado lógico sobre `usuarios`.

Una alternativa sería agregar una columna booleana `activo` mediante una migración SQL. En ese caso, en lugar de eliminar el registro, se actualizaría su estado:

```sql
UPDATE usuarios
SET activo = FALSE
WHERE usuario_id = 1;
```

Esta alternativa es una propuesta y no se ejecutó sobre la base de datos actual.

### 2.4.4 Transacción con punto de recuperación

Se realizó una transacción que modificó dos tablas relacionadas: `usuarios` y `usuario_estandar`.

```sql
BEGIN;

INSERT INTO usuarios (usuario_id, correo, nombre, apellidos, tipo_usuario)
VALUES (999999, 'transaccion@ejemplo.com', 'Usuario', 'Temporal', 'estandar');

INSERT INTO usuario_estandar (usuario_id, tipo_usuario, limite_resenas)
VALUES (999999, 'estandar', 0);

SAVEPOINT punto_control;

UPDATE usuarios
SET nombre = 'Cambio temporal'
WHERE usuario_id = 999999;

UPDATE usuario_estandar
SET limite_resenas = 10
WHERE usuario_id = 999999;

ROLLBACK TO SAVEPOINT punto_control;

COMMIT;
```

**Resultado:** Se insertaron los registros en ambas tablas. Después, se realizaron dos modificaciones y se utilizó `ROLLBACK TO SAVEPOINT` para deshacerlas sin cancelar las inserciones iniciales. Finalmente, `COMMIT` confirmó los cambios restantes.

Se verificó el resultado mediante una consulta a las dos tablas. El usuario conservó el nombre `Usuario` y el límite de reseñas `0`.

Esto demuestra que un punto de recuperación permite revertir una parte de una transacción y conservar las operaciones anteriores al punto de control.

### 2.4.5 Transacción que falla por una restricción

Se realizó una transacción que primero modificó el nombre de un usuario y después intentó asignar un límite de reseñas negativo.

```sql
BEGIN;

UPDATE usuarios
SET nombre = 'Cambio que debe revertirse'
WHERE usuario_id = 999999;

UPDATE usuario_estandar
SET limite_resenas = -1
WHERE usuario_id = 999999;

COMMIT;
```

**Mensaje devuelto por PostgreSQL:**

```text
ERROR: new row for relation "usuario_estandar"
violates check constraint "ck_usuario_estandar_limite"
DETAIL: Failing row contains (999999, estandar, -1, t).
```

La restricción `ck_usuario_estandar_limite` rechazó el valor negativo. Como la segunda operación falló, PostgreSQL marcó la transacción como fallida. Al finalizar la conexión, los cambios pendientes se revirtieron automáticamente.

**Comprobación:**

Se consultaron nuevamente las tablas `usuarios` y `usuario_estandar`:

| usuario_id | nombre | limite_resenas |
|---:|---|---:|
| 999999 | Usuario | 0 |

El resultado confirmó que el primer `UPDATE` tampoco quedó guardado. Por lo tanto, la base de datos conservó el estado que tenía antes de iniciar la transacción.

### 2.4.3 Eliminación física y eliminación lógica

**A) Eliminación física mediante DELETE**

Se realizó una eliminación utilizando una subconsulta para localizar al usuario temporal con identificador `999999`.

```sql
DELETE FROM usuarios
WHERE usuario_id IN (
    SELECT usuario_id
    FROM usuario_estandar
    WHERE usuario_id = 999999
);
```

**Resultado:** `DELETE 1`.

Se comprobó que el usuario ya no existía en `usuarios` ni en `usuario_estandar`. La eliminación del registro relacionado se realizó mediante la restricción `ON DELETE CASCADE`.

**B) Eliminación lógica mediante UPDATE**

Se agregó la columna `activo` a la tabla `usuarios`, mediante la migración `004_agregar_activo_usuarios.sql`, con valor predeterminado `TRUE`.

Se creó un usuario temporal con identificador `999998` y posteriormente se marcó como inactivo:

```sql
UPDATE usuarios
SET activo = FALSE
WHERE usuario_id = 999998;
```

**Resultado:** `UPDATE 1`.

La consulta de comprobación mostró que el usuario continúa almacenado en la tabla, pero su columna `activo` tiene el valor `FALSE`.

**Conclusión:** DELETE elimina físicamente el registro, mientras que la eliminación lógica conserva la información y utiliza una columna de estado para identificar los registros inactivos.