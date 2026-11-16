## Caso 1: Violación de restricción NOT NULL en campos obligatorios
* **Descripción:** Se intenta insertar una tupla en la tabla `playlist` omitiendo el nombre obligatorio.
* **Sentencia SQL:**
  ```sql
  INSERT INTO playlist (identificador_id, nombre) VALUES (1, NULL);
  *Resultado esperado: Fallo en la inserción.*

Mensaje de PostgreSQL: ERROR: el valor nulo en la columna "nombre" viola la restricción not-null

Regla protegida: Obligatoriedad de los atributos esenciales en la entidad playlist.
* **Evidencia** *
<img width="1440" height="124" alt="Caso1" src="https://github.com/user-attachments/assets/31f52036-767b-401d-b310-97a0dd816013" />

### Caso 2: Comprobación de valor DEFAULT automático
* **Descripción:** Se registra un usuario omitiendo la fecha de registro para verificar la asignación por defecto.
* **Sentencia SQL:**
  ```sql
  INSERT INTO usuarios (usuario_id, correo, nombre, apellidos, tipo_usuario) VALUES (1, 'test@example.com', 'Juan', 'Pérez', 'estandar');
  SELECT fecha_registro FROM usuarios WHERE usuario_id = 1;
  ```
* **Resultado esperado:** Inserción exitosa asignando la fecha actual del sistema.
* **Mensaje de PostgreSQL:** `INSERT 0 1` y devuelve la fecha actual gracias a `CURRENT_DATE`.
* **Regla protegida:** Automatización del registro temporal en la tabla `usuarios`.
* **Evidencia* **
  <img width="1449" height="254" alt="image" src="https://github.com/user-attachments/assets/adac46d8-3b80-4038-9e52-d99690979164" />

### Caso 3: Violación de restricción UNIQUE simple
* **Descripción:** Se intenta registrar dos usuarios diferentes utilizando exactamente el mismo correo electrónico.
* **Sentencia SQL:**
  ```sql
  INSERT INTO usuarios (usuario_id, correo, nombre, apellidos) VALUES (1, 'correo@mail.com', 'Ana', 'Gómez');
  INSERT INTO usuarios (usuario_id, correo, nombre, apellidos) VALUES (2, 'correo@mail.com', 'Carlos', 'Ruíz');
  ```
* **Resultado esperado:** Rechazo del segundo registro.
* **Mensaje de PostgreSQL:** `ERROR: duplicar valor de llave viola la restricción de unicidad «uq_usuarios_correo»`
* **Regla protegida:** Unicidad del correo electrónico por cada usuario registrado.

* **Evidencia** *
<img width="1450" height="159" alt="image" src="https://github.com/user-attachments/assets/8b51deab-4e0d-43eb-b357-bec3697ac9b4" />

### Caso 4: Violación de clave única compuesta
* **Descripción:** Se intenta duplicar la combinación de clave en la producción audiovisual.
* **Sentencia SQL:**
  ```sql
  INSERT INTO produccion_audiovisual (contenido_id, titulo, tipo_produccion) VALUES (10, 'Película A', 'pelicula');
  INSERT INTO produccion_audiovisual (contenido_id, titulo, tipo_produccion) VALUES (10, 'Película B', 'pelicula');
  ```
* **Resultado esperado:** Fallo por duplicidad en la llave combinada.
* **Mensaje de PostgreSQL:** `ERROR: duplicar valor de llave viola la restricción de unicidad «uq_produccion_id_tipo»`
* **Regla protegida:** Consistencia en la identificación del supertipo y subtipo audiovisual.

* **Evidencia* **
<img width="1443" height="133" alt="image" src="https://github.com/user-attachments/assets/f6981bb8-8b66-4b88-aaea-3443403f95b9" />

### Caso 5: Violación de CHECK de rango numérico en años
* **Descripción:** Se intenta registrar un libro con un año de publicación fuera del rango histórico permitido.
* **Sentencia SQL:**
  ```sql
  INSERT INTO libros (libro_id, titulo, anio_publicacion, autor_id) VALUES (2, 'Libro Futuro', 2500, 1);
  ```
* **Resultado esperado:** Rechazo de la fila por salir del rango permitido.
* **Mensaje de PostgreSQL:** `ERROR: la nueva fila de la relación «libros» viola la restricción «ck_libros_anio»`
* **Regla protegida:** Validez temporal del año de publicación (del 1 al 2100).

* **Evidencia** *
<img width="1443" height="76" alt="image" src="https://github.com/user-attachments/assets/53b70387-decc-4c54-a74c-733163d79e63" />

### Caso 6: Violación de CHECK de formato de texto (correo)
* **Descripción:** Se intenta insertar un usuario con una dirección de correo electrónico que carece del símbolo `@`.
* **Sentencia SQL:**
  ```sql
  INSERT INTO usuarios (usuario_id, correo, nombre, apellidos) VALUES (3, 'correosinarroba.com', 'Maria', 'Lopez');
  ```
* **Resultado esperado:** Fallo en la validación del patrón de texto.
* **Mensaje de PostgreSQL:** `ERROR: la nueva fila de la relación «usuarios» viola la restricción «ck_usuarios_correo»`
* **Regla protegida:** Obligatoriedad de que el correo contenga el carácter `@`.
* **Evidencia* **
  <img width="1460" height="107" alt="image" src="https://github.com/user-attachments/assets/639d101f-ef7e-4be4-bdc9-727bd2e09794" />

### Caso 7: Violación de CHECK de dominio cerrado (tipo_usuario)
* **Descripción:** Se inserta un tipo de usuario no incluido dentro del conjunto cerrado permitido.
* **Sentencia SQL:**
  ```sql
  INSERT INTO usuarios (usuario_id, correo, nombre, apellidos, tipo_usuario) VALUES (4, 'admin@mail.com', 'Pedro', 'Infante', 'superadmin');
  ```
* **Resultado esperado:** Rechazo al no pertenecer a las opciones permitidas.
* **Mensaje de PostgreSQL:** `ERROR: la nueva fila de la relación «usuarios» viola la restricción «ck_usuarios_tipo»`
* **Regla protegida:** Restricción estricta a los tipos válidos (`estandar`, `premium`).

* **Evidencia** *

<img width="1448" height="95" alt="image" src="https://github.com/user-attachments/assets/5c1c9169-e167-4421-9ee4-9578e938496c" />

### Caso 8: Violación de integridad referencial (Llave Foránea)
* **Descripción:** Se intenta registrar un libro asociándolo a un autor que no existe en el sistema.
* **Sentencia SQL:**
  ```sql
  INSERT INTO libros (libro_id, titulo, anio_publicacion, autor_id) VALUES (3, 'Libro Huérfano', 2022, 9999);
  ```
* **Resultado esperado:** Error de integridad referencial por clave inexistente.
* **Mensaje de PostgreSQL:** `ERROR: inserción o actualización en la tabla «libros» viola la llave foránea «fk_libros_autor»`
* **Regla protegida:** Todo libro debe estar asociado obligatoriamente a un autor registrado previamente.
* **Evidencia* **
<img width="1443" height="108" alt="image" src="https://github.com/user-attachments/assets/315e19c4-b0cb-4983-af1b-3bc321c2c5a7" />

### Caso 9: Violación de CHECK de rango decimal en porcentajes
* **Descripción:** Se intenta registrar un porcentaje de avance superior al 100% en la tabla de visualización.
* **Sentencia SQL:**
  ```sql
  INSERT INTO visualiza (usuario_id, contenido_id, porcentaje_avance, fecha_reproduccion, estado) VALUES (1, 10, 150.00, CURRENT_TIMESTAMP, 'pausado');
  ```
* **Resultado esperado:** Fallo por superar el límite superior del porcentaje.
* **Mensaje de PostgreSQL:** `ERROR: la nueva fila de la relación «visualiza» viola la restricción «ck_visualiza_avance»`
* **Regla protegida:** El porcentaje de avance en la reproducción debe encontrarse estrictamente entre 0 y 100.

* **Evidencia** *
<img width="1438" height="117" alt="image" src="https://github.com/user-attachments/assets/0d1133b9-f911-421f-988f-301c417f0e67" />

### Caso 10: Violación de CHECK condicional entre múltiples columnas
* **Descripción:** Se intenta registrar una obra basada en otra dejando nulos tanto el campo de libro como el de cómic.
* **Sentencia SQL:**
  ```sql
  INSERT INTO esta_basada_en (contenido_id, libro_id, comic_id) VALUES (10, NULL, NULL);
  ```
* **Resultado esperado:** Rechazo por no cumplir la condición lógica de origen.
* **Mensaje de PostgreSQL:** `ERROR: la nueva fila de la relación «esta_basada_en» viola la restricción «ck_basada_en_origen»`
* **Regla protegida:** Toda producción basada en otra obra debe apuntar obligatoriamente a un libro o a un cómic válido (al menos uno no nulo).

* **Evidencia** *
<img width="1455" height="97" alt="image" src="https://github.com/user-attachments/assets/5c937054-206a-4597-b9df-b0e9ba7ed3a0" />






