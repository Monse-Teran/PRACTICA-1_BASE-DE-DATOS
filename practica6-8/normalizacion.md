# Prácticas 6, 7 y 8 — Normalización de bases de datos

**Proyecto:** Club de Streaming Independiente

# Ejercicio 1.1. Pautas de diseño

En este apartado se describe qué representa cada tabla del proyecto y se evalúa su estructura mediante cuatro pautas: semántica clara, ausencia de anomalías, pocos valores nulos y ausencia de tuplas espurias.

## 1. Tabla `playlist`

**Descripción:** Cada fila representa una playlist musical registrada en la plataforma. Se identifica mediante `identificador_id` y almacena su nombre y un enlace opcional.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| identificador_id | INTEGER | PRIMARY KEY, NOT NULL |
| nombre | VARCHAR(80) | NOT NULL |
| enlace | VARCHAR(255) | Permite NULL |

**Evaluación:**

- **Semántica clara:** Cumple. La tabla representa una lista de reproducción musical.
- **Ausencia de anomalías:** No se identifican anomalías evidentes dentro de la tabla. Sin embargo, el esquema no garantiza que toda playlist esté asociada a una producción audiovisual.
- **Pocos valores nulos:** El atributo `enlace` permite NULL porque es opcional.
- **Ausencia de tuplas espurias:** La asociación con `produccion_audiovisual` debe comprobarse mediante una reunión. La restricción UNIQUE evita asignar una misma playlist a varias producciones, pero no obliga a que toda playlist esté relacionada.

## 2. Tabla `autores`

**Descripción:** Cada fila representa un autor registrado en el catálogo. Se identifica mediante `autor_id` y puede almacenar información biográfica.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| autor_id | INTEGER | PRIMARY KEY, NOT NULL |
| biografia | TEXT | Permite NULL |

**Evaluación:**

- **Semántica clara:** Cumple. La tabla representa autores y almacena sus datos descriptivos.
- **Ausencia de anomalías:** Cumple. Los datos de cada autor se almacenan una sola vez y los libros y cómics conservan únicamente su identificador.
- **Pocos valores nulos:** `biografia` permite NULL porque la información biográfica es opcional.
- **Ausencia de tuplas espurias:** La reunión con `libros` y `comics` se realiza mediante `autor_id`, que es clave primaria en esta tabla.

## 3. Tabla `libros`

**Descripción:** Cada fila representa un libro registrado en la plataforma. Se identifica mediante `libro_id` y almacena su título, año de publicación y el identificador de su autor.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| libro_id | INTEGER | PRIMARY KEY, NOT NULL |
| titulo | VARCHAR(150) | NOT NULL |
| anio_publicacion | INTEGER | Permite NULL |
| autor_id | INTEGER | FOREIGN KEY, NOT NULL |

**Evaluación:**

- **Semántica clara:** Cumple. Los atributos describen un libro e identifican al autor relacionado.
- **Ausencia de anomalías:** Cumple. Los datos del autor se almacenan en la tabla `autores`, evitando repetir su información en cada libro.
- **Pocos valores nulos:** `anio_publicacion` permite NULL cuando el año es desconocido o no se registra.
- **Ausencia de tuplas espurias:** La reunión con `autores` se realiza mediante `autor_id`, que es clave primaria de esa tabla.

## 4. Tabla `comics`

**Descripción:** Cada fila representa un cómic registrado en el catálogo. Se identifica mediante `comic_id` y almacena su título, número de edición y el identificador de su autor.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| comic_id | INTEGER | PRIMARY KEY, NOT NULL |
| titulo | VARCHAR(150) | NOT NULL |
| numero_edicion | INTEGER | Permite NULL |
| autor_id | INTEGER | FOREIGN KEY, NOT NULL |

**Evaluación:**

- **Semántica clara:** Cumple. La tabla representa cómics y sus características.
- **Ausencia de anomalías:** Cumple. La información del autor se mantiene en `autores` y no se duplica en cada cómic.
- **Pocos valores nulos:** `numero_edicion` permite NULL cuando no se conoce o no se registra el número de edición.
- **Ausencia de tuplas espurias:** La reunión con `autores` se realiza mediante la clave primaria `autor_id` de esa tabla.

## 5. Tabla `usuarios`

**Descripción:** Cada fila representa una persona registrada en la plataforma. Se identifica mediante `usuario_id` y almacena su correo, fecha de registro, nombre, apellidos, tipo de usuario y estado de actividad.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| usuario_id | INTEGER | PRIMARY KEY, NOT NULL |
| correo | VARCHAR(120) | NOT NULL, UNIQUE |
| fecha_registro | DATE | NOT NULL, DEFAULT CURRENT_DATE |
| nombre | VARCHAR(60) | NOT NULL |
| apellidos | VARCHAR(100) | NOT NULL |
| tipo_usuario | VARCHAR(10) | Permite NULL |
| activo | BOOLEAN | NOT NULL, DEFAULT TRUE; agregado por migración 004 |

**Evaluación:**

- **Semántica clara:** Cumple. La tabla representa el supertipo de usuarios y almacena sus datos generales.
- **Ausencia de anomalías:** Cumple parcialmente. `usuario_id` identifica cada usuario y `correo` es único. Sin embargo, los requisitos establecen una especialización total y disjunta entre usuarios estándar y premium, mientras que `tipo_usuario` permite NULL.
- **Pocos valores nulos:** `tipo_usuario` permite NULL, aunque los requisitos indican que todos los usuarios deben pertenecer a uno de los dos subtipos.
- **Ausencia de tuplas espurias:** La reunión con las tablas de usuarios estándar y premium debe comprobarse mediante sus claves y el discriminador correspondiente.

## 6. Tabla `usuario_estandar`

**Descripción:** Cada fila representa un usuario perteneciente al subtipo estándar. Almacena su identificador, tipo de usuario, límite de reseñas y configuración de publicidad.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| usuario_id | INTEGER | PRIMARY KEY, NOT NULL, FOREIGN KEY |
| tipo_usuario | VARCHAR(10) | NOT NULL, DEFAULT 'estandar' |
| limite_resenas | INTEGER | NOT NULL, CHECK >= 0 |
| publicidad | BOOLEAN | NOT NULL, DEFAULT TRUE |

**Evaluación:**

- **Semántica clara:** Cumple. La tabla representa las características propias de los usuarios estándar.
- **Ausencia de anomalías:** Cumple estructuralmente. La clave primaria identifica cada usuario estándar y la llave foránea lo relaciona con `usuarios`.
- **Pocos valores nulos:** Cumple. Todos los atributos son NOT NULL.
- **Ausencia de tuplas espurias:** La relación con `usuarios` utiliza `(usuario_id, tipo_usuario)`, combinación declarada UNIQUE en la tabla principal.

## 7. Tabla `usuario_premium`

**Descripción:** Cada fila representa un usuario perteneciente al subtipo premium. Almacena su identificador, tipo de usuario, método de pago y fecha de renovación.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| usuario_id | INTEGER | PRIMARY KEY, NOT NULL, FOREIGN KEY |
| tipo_usuario | VARCHAR(10) | NOT NULL, DEFAULT 'premium' |
| metodo_pago | VARCHAR(30) | NOT NULL |
| fecha_renovacion | DATE | Permite NULL |

**Evaluación:**

- **Semántica clara:** Cumple. La tabla representa las características particulares de los usuarios premium.
- **Ausencia de anomalías:** Cumple estructuralmente. La clave primaria identifica a cada usuario premium y la llave foránea lo relaciona con `usuarios`.
- **Pocos valores nulos:** `fecha_renovacion` permite NULL cuando no se registra una fecha.
- **Ausencia de tuplas espurias:** La relación con `usuarios` utiliza `(usuario_id, tipo_usuario)` y la restricción CHECK exige que el tipo sea premium.

## 8. Tabla `produccion_audiovisual`

**Descripción:** Cada fila representa una producción audiovisual del catálogo, que puede ser película o serie. Almacena su identificador, título, año de estreno, director, tipo de producción y una playlist asociada.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| contenido_id | INTEGER | PRIMARY KEY, NOT NULL |
| titulo | VARCHAR(150) | NOT NULL |
| anio_estreno | INTEGER | Permite NULL |
| director | VARCHAR(100) | Permite NULL |
| tipo_produccion | VARCHAR(10) | Permite NULL |
| playlist_id | INTEGER | FOREIGN KEY, UNIQUE, permite NULL |

**Evaluación:**

- **Semántica clara:** Cumple. Representa el supertipo de las producciones audiovisuales y almacena los atributos comunes.
- **Ausencia de anomalías:** Cumple parcialmente. Los datos generales están separados de los atributos específicos de películas y series. Sin embargo, `tipo_produccion` permite NULL, aunque los requisitos establecen una especialización total y disjunta.
- **Pocos valores nulos:** `anio_estreno`, `director`, `tipo_produccion` y `playlist_id` permiten NULL.
- **Ausencia de tuplas espurias:** Las reuniones con `peliculas`, `series` y `produccion_generos` deben comprobarse mediante las claves correspondientes.

## 9. Tabla `produccion_generos`

**Descripción:** Cada fila representa un género asociado a una producción audiovisual. Permite registrar varios géneros para una misma producción sin almacenar una lista de valores en una sola columna.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| contenido_id | INTEGER | PRIMARY KEY compuesta, FOREIGN KEY, NOT NULL |
| genero | VARCHAR(40) | PRIMARY KEY compuesta, NOT NULL |

**Evaluación:**

- **Semántica clara:** Cumple. Representa la asociación entre producciones y géneros.
- **Ausencia de anomalías:** Cumple. La clave primaria compuesta evita repetir el mismo género para una producción.
- **Pocos valores nulos:** Cumple. Ambos atributos son NOT NULL.
- **Ausencia de tuplas espurias:** La reunión con `produccion_audiovisual` se realiza mediante `contenido_id`, que es clave primaria de la producción.

## 10. Tabla `peliculas`

**Descripción:** Cada fila representa una película del catálogo. Es un subtipo de `produccion_audiovisual` y almacena su identificador, tipo de producción y duración.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| contenido_id | INTEGER | PRIMARY KEY, NOT NULL, FOREIGN KEY |
| tipo_produccion | VARCHAR(10) | NOT NULL, DEFAULT 'pelicula' |
| duracion | INTEGER | Permite NULL, CHECK > 0 |

**Evaluación:**

- **Semántica clara:** Cumple. Representa las películas y sus atributos particulares.
- **Ausencia de anomalías:** Cumple parcialmente. `tipo_produccion` repite un valor constante para identificar el subtipo; la información general se conserva en `produccion_audiovisual`.
- **Pocos valores nulos:** `duracion` permite NULL cuando no se registra este dato.
- **Ausencia de tuplas espurias:** La reunión con `produccion_audiovisual` se realiza mediante `(contenido_id, tipo_produccion)`.

## 11. Tabla `pelicula_idiomas`

**Descripción:** Cada fila representa un idioma de audio disponible para una película. Permite registrar múltiples idiomas para una misma película.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| contenido_id | INTEGER | PRIMARY KEY compuesta, FOREIGN KEY, NOT NULL |
| idioma | VARCHAR(40) | PRIMARY KEY compuesta, NOT NULL |

**Evaluación:**

- **Semántica clara:** Cumple. Representa los idiomas de audio disponibles para cada película.
- **Ausencia de anomalías:** Cumple. La clave compuesta evita duplicar el mismo idioma para una misma película.
- **Pocos valores nulos:** Cumple. Ambos atributos son NOT NULL.
- **Ausencia de tuplas espurias:** La reunión con `peliculas` se realiza mediante `contenido_id`, que es clave primaria de esa tabla.

## 12. Tabla `series`

**Descripción:** Cada fila representa una serie del catálogo. Es un subtipo de `produccion_audiovisual` y almacena su identificador, tipo, número de temporadas y número de capítulos.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| contenido_id | INTEGER | PRIMARY KEY, NOT NULL, FOREIGN KEY |
| tipo_produccion | VARCHAR(10) | NOT NULL, DEFAULT 'serie' |
| num_temporadas | INTEGER | Permite NULL, CHECK > 0 |
| num_capitulos | INTEGER | Permite NULL, CHECK > 0 |

**Evaluación:**

- **Semántica clara:** Cumple. Representa series y sus características particulares.
- **Ausencia de anomalías:** Cumple parcialmente. `tipo_produccion` repite un valor constante que identifica el subtipo; los datos generales se mantienen en `produccion_audiovisual`.
- **Pocos valores nulos:** `num_temporadas` y `num_capitulos` permiten NULL.
- **Ausencia de tuplas espurias:** La reunión con `produccion_audiovisual` se realiza mediante `(contenido_id, tipo_produccion)`.

## 13. Tabla `resenas`

**Descripción:** Cada fila representa una reseña escrita por un usuario sobre una producción audiovisual. Almacena su identificador, puntuación, comentario, fecha, usuario que la escribió y producción evaluada.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| resena_id | INTEGER | PRIMARY KEY, NOT NULL |
| puntuacion | INTEGER | NOT NULL, CHECK entre 1 y 5 |
| comentario | TEXT | Permite NULL |
| fecha | DATE | NOT NULL, DEFAULT CURRENT_DATE |
| usuario_id | INTEGER | FOREIGN KEY, NOT NULL |
| contenido_id | INTEGER | FOREIGN KEY, NOT NULL |

**Evaluación:**

- **Semántica clara:** Cumple. Representa las reseñas e identifica al usuario y la producción relacionada.
- **Ausencia de anomalías:** Cumple estructuralmente. Cada reseña tiene una clave propia y las llaves foráneas mantienen la integridad referencial.
- **Pocos valores nulos:** `comentario` permite NULL porque una reseña puede tener puntuación sin texto.
- **Ausencia de tuplas espurias:** Las reuniones con `usuarios` y `produccion_audiovisual` se realizan mediante sus claves primarias.

## 14. Tabla `visualiza`

**Descripción:** Cada fila representa el registro de visualización de una producción por parte de un usuario. Almacena el usuario, la producción, el porcentaje de avance, la fecha de reproducción y el estado.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| usuario_id | INTEGER | PRIMARY KEY compuesta, FOREIGN KEY, NOT NULL |
| contenido_id | INTEGER | PRIMARY KEY compuesta, FOREIGN KEY, NOT NULL |
| porcentaje_avance | DECIMAL(5,2) | NOT NULL, DEFAULT 0 |
| fecha_reproduccion | TIMESTAMP | NOT NULL |
| estado | VARCHAR(10) | NOT NULL, CHECK pausado o terminado |

**Evaluación:**

- **Semántica clara:** Cumple. Representa la relación muchos a muchos entre usuarios y producciones audiovisuales.
- **Ausencia de anomalías:** Cumple parcialmente. La clave primaria compuesta permite solamente un registro por combinación de usuario y producción. Si se necesita guardar varias sesiones de reproducción de una misma producción por un usuario, la clave actual no lo permite.
- **Pocos valores nulos:** Cumple. Todos sus atributos son NOT NULL.
- **Ausencia de tuplas espurias:** Las reuniones con `usuarios` y `produccion_audiovisual` se realizan mediante sus claves primarias.

## 15. Tabla `esta_basada_en`

**Descripción:** Cada fila representa la relación entre una producción audiovisual y el libro o cómic en el que está basada. Se identifica mediante `contenido_id` y almacena los identificadores de las obras relacionadas.

| Atributo | Tipo de dato | Restricciones |
|---|---|---|
| contenido_id | INTEGER | PRIMARY KEY, FOREIGN KEY, NOT NULL |
| libro_id | INTEGER | FOREIGN KEY, permite NULL |
| comic_id | INTEGER | FOREIGN KEY, permite NULL |

**Evaluación:**

- **Semántica clara:** Cumple parcialmente. La tabla representa la obra de origen de una producción. El esquema permite asociar un libro, un cómic o ambos.
- **Ausencia de anomalías:** Cumple estructuralmente. `contenido_id` limita a una fila por producción.
- **Pocos valores nulos:** `libro_id` y `comic_id` permiten NULL. El CHECK exige que al menos uno tenga valor, pero permite que ambos estén informados.
- **Ausencia de tuplas espurias:** Las relaciones con producciones, libros y cómics se realizan mediante sus respectivas claves primarias.

### Conclusión del ejercicio 1.1

El esquema separa las entidades principales, los subtipos y los atributos multivaluados. Se identificaron diferencias entre algunas restricciones SQL y las reglas del negocio, como la especialización total de usuarios y producciones y la participación obligatoria de las playlists.

La cantidad real de valores nulos debe determinarse consultando los datos existentes. La ausencia de tuplas espurias se comprobará formalmente mediante las reuniones y las descomposiciones correspondientes.

---

# Ejercicio 1.2. Dependencias funcionales

## 1.2.1. Conjunto de dependencias funcionales

Las dependencias funcionales se establecen a partir de las reglas del negocio, las claves y las restricciones declaradas en el esquema. No se deducen de los datos de ejemplo.

Una dependencia funcional se representa como:

\[
X \rightarrow Y
\]

Significa que el valor del conjunto de atributos X determina de manera única el valor del conjunto de atributos Y.

### 1. `playlist`

Relación: `playlist(identificador_id, nombre, enlace)`.

\[
identificador\_id \rightarrow nombre
\]

\[
identificador\_id \rightarrow enlace
\]

**Justificación:** Cada playlist tiene un identificador propio que permite recuperar su nombre y enlace.

### 2. `autores`

Relación: `autores(autor_id, biografia)`.

\[
autor\_id \rightarrow biografia
\]

**Justificación:** Cada autor se identifica mediante un identificador único que determina su información biográfica.

### 3. `libros`

Relación: `libros(libro_id, titulo, anio_publicacion, autor_id)`.

\[
libro\_id \rightarrow titulo
\]

\[
libro\_id \rightarrow anio\_publicacion
\]

\[
libro\_id \rightarrow autor\_id
\]

**Justificación:** Cada libro tiene un identificador único, un título y un año de publicación. Cada libro pertenece a un autor, aunque un autor puede escribir varios libros.

### 4. `comics`

Relación: `comics(comic_id, titulo, numero_edicion, autor_id)`.

\[
comic\_id \rightarrow titulo
\]

\[
comic\_id \rightarrow numero\_edicion
\]

\[
comic\_id \rightarrow autor\_id
\]

**Justificación:** Cada cómic tiene un identificador único y pertenece a un autor. Un autor puede tener varios cómics registrados.

### 5. `usuarios`

Relación: `usuarios(usuario_id, correo, fecha_registro, nombre, apellidos, tipo_usuario, activo)`.

\[
usuario\_id \rightarrow correo
\]

\[
usuario\_id \rightarrow fecha\_registro
\]

\[
usuario\_id \rightarrow nombre
\]

\[
usuario\_id \rightarrow apellidos
\]

\[
usuario\_id \rightarrow tipo\_usuario
\]

\[
usuario\_id \rightarrow activo
\]

\[
correo \rightarrow usuario\_id
\]

**Justificación:** `usuario_id` es la clave primaria y determina los atributos del usuario. Además, `correo` es UNIQUE y NOT NULL, por lo que cada correo corresponde a un solo usuario. El atributo conceptual `nombre_completo` se representa mediante `nombre` y `apellidos`.

### 6. `usuario_estandar`

Relación: `usuario_estandar(usuario_id, tipo_usuario, limite_resenas, publicidad)`.

\[
usuario\_id \rightarrow tipo\_usuario
\]

\[
usuario\_id \rightarrow limite\_resenas
\]

\[
usuario\_id \rightarrow publicidad
\]

**Justificación:** Cada usuario estándar se identifica mediante `usuario_id`, que determina sus atributos propios. El tipo de usuario está restringido al valor `estandar`.

### 7. `usuario_premium`

Relación: `usuario_premium(usuario_id, tipo_usuario, metodo_pago, fecha_renovacion)`.

\[
usuario\_id \rightarrow tipo\_usuario
\]

\[
usuario\_id \rightarrow metodo\_pago
\]

\[
usuario\_id \rightarrow fecha\_renovacion
\]

**Justificación:** Cada usuario premium se identifica mediante `usuario_id`, que determina sus atributos particulares. El tipo está restringido al valor `premium`.

### 8. `produccion_audiovisual`

Relación: `produccion_audiovisual(contenido_id, titulo, anio_estreno, director, tipo_produccion, playlist_id)`.

\[
contenido\_id \rightarrow titulo
\]

\[
contenido\_id \rightarrow anio\_estreno
\]

\[
contenido\_id \rightarrow director
\]

\[
contenido\_id \rightarrow tipo\_produccion
\]

\[
contenido\_id \rightarrow playlist\_id
\]

**Justificación:** Cada producción audiovisual tiene un identificador único que determina sus datos generales y su playlist asociada, cuando existe.

### 9. `produccion_generos`

Relación: `produccion_generos(contenido_id, genero)`.

No existen dependencias funcionales no triviales entre los dos atributos.

**Justificación:** Una producción puede tener varios géneros y un mismo género puede asociarse a distintas producciones. Ninguno de los atributos determina al otro por separado.

La clave está formada por:

\[
(contenido\_id,genero)
\]

### 10. `peliculas`

Relación: `peliculas(contenido_id, tipo_produccion, duracion)`.

\[
contenido\_id \rightarrow tipo\_produccion
\]

\[
contenido\_id \rightarrow duracion
\]

**Justificación:** Cada película tiene un identificador de producción único que determina sus datos específicos. El tipo está restringido al valor `pelicula`.

### 11. `pelicula_idiomas`

Relación: `pelicula_idiomas(contenido_id, idioma)`.

No existen dependencias funcionales no triviales entre los dos atributos.

**Justificación:** Una película puede tener varios idiomas de audio y un mismo idioma puede estar presente en varias películas. Ninguno de los atributos determina al otro por separado.

La clave está formada por:

\[
(contenido\_id,idioma)
\]

### 12. `series`

Relación: `series(contenido_id, tipo_produccion, num_temporadas, num_capitulos)`.

\[
contenido\_id \rightarrow tipo\_produccion
\]

\[
contenido\_id \rightarrow num\_temporadas
\]

\[
contenido\_id \rightarrow num\_capitulos
\]

**Justificación:** Cada serie tiene un identificador único que determina sus atributos específicos. El tipo está restringido al valor `serie`.

### 13. `resenas`

Relación: `resenas(resena_id, puntuacion, comentario, fecha, usuario_id, contenido_id)`.

\[
resena\_id \rightarrow puntuacion
\]

\[
resena\_id \rightarrow comentario
\]

\[
resena\_id \rightarrow fecha
\]

\[
resena\_id \rightarrow usuario\_id
\]

\[
resena\_id \rightarrow contenido\_id
\]

**Justificación:** Cada reseña tiene un identificador propio que determina su puntuación, comentario, fecha, usuario emisor y producción evaluada. No se considera que `(usuario_id, contenido_id)` sea clave porque el esquema no establece una restricción UNIQUE sobre esa combinación.

### 14. `visualiza`

Relación: `visualiza(usuario_id, contenido_id, porcentaje_avance, fecha_reproduccion, estado)`.

\[
(usuario\_id,contenido\_id) \rightarrow porcentaje\_avance
\]

\[
(usuario\_id,contenido\_id) \rightarrow fecha\_reproduccion
\]

\[
(usuario\_id,contenido\_id) \rightarrow estado
\]

**Justificación:** La clave primaria compuesta identifica el registro de visualización de una producción por parte de un usuario. Esta dependencia corresponde al diseño actual, que permite un solo registro por combinación de usuario y producción.

### 15. `esta_basada_en`

Relación: `esta_basada_en(contenido_id, libro_id, comic_id)`.

\[
contenido\_id \rightarrow libro\_id
\]

\[
contenido\_id \rightarrow comic\_id
\]

**Justificación:** Cada producción participa como máximo una vez en esta relación porque `contenido_id` es la clave primaria. Por ello, determina los identificadores del libro o cómic asociado.

## 1.2.2. Cierres de atributos y claves candidatas

El cierre de un conjunto de atributos X, representado como X+, contiene los atributos que pueden determinarse a partir de X. Si el cierre contiene todos los atributos de la relación, el conjunto es una superclave. Si además es mínimo, es una clave candidata.

### 1. `playlist`

Se inicia con:

\[
C_0=\{identificador\_id\}
\]

Aplicando las dependencias funcionales:

\[
C_1=\{identificador\_id,nombre,enlace\}
\]

Por lo tanto:

\[
identificador\_id^+=\{identificador\_id,nombre,enlace\}
\]

**Clave candidata:** `{identificador_id}`.

### 2. `autores`

Se inicia con:

\[
C_0=\{autor\_id\}
\]

Aplicando la dependencia funcional:

\[
C_1=\{autor\_id,biografia\}
\]

\[
autor\_id^+=\{autor\_id,biografia\}
\]

**Clave candidata:** `{autor_id}`.

### 3. `libros`

Se inicia con:

\[
C_0=\{libro\_id\}
\]

Aplicando las dependencias funcionales:

\[
C_1=\{libro\_id,titulo,anio\_publicacion,autor\_id\}
\]

\[
libro\_id^+=\{libro\_id,titulo,anio\_publicacion,autor\_id\}
\]

**Clave candidata:** `{libro_id}`.

### 4. `comics`

Se inicia con:

\[
C_0=\{comic\_id\}
\]

Aplicando las dependencias funcionales:

\[
C_1=\{comic\_id,titulo,numero\_edicion,autor\_id\}
\]

\[
comic\_id^+=\{comic\_id,titulo,numero\_edicion,autor\_id\}
\]

**Clave candidata:** `{comic_id}`.

### 5. `usuarios`

Primer cierre, a partir de la clave primaria:

\[
C_0=\{usuario\_id\}
\]

Aplicando las dependencias desde `usuario_id`:

\[
C_1=\{usuario\_id,correo,fecha\_registro,nombre,apellidos,tipo\_usuario,activo\}
\]

\[
usuario\_id^+=\{usuario\_id,correo,fecha\_registro,nombre,apellidos,tipo\_usuario,activo\}
\]

Segundo cierre, a partir del correo:

\[
C_0=\{correo\}
\]

Por `correo → usuario_id`:

\[
C_1=\{correo,usuario\_id\}
\]

A partir de `usuario_id` se obtienen los demás atributos:

\[
C_2=\{correo,usuario\_id,fecha\_registro,nombre,apellidos,tipo\_usuario,activo\}
\]

**Claves candidatas:** `{usuario_id}` y `{correo}`.

### 6. `usuario_estandar`

Se inicia con:

\[
C_0=\{usuario\_id\}
\]

Aplicando las dependencias:

\[
C_1=\{usuario\_id,tipo\_usuario,limite\_resenas,publicidad\}
\]

\[
usuario\_id^+=\{usuario\_id,tipo\_usuario,limite\_resenas,publicidad\}
\]

**Clave candidata:** `{usuario_id}`.

### 7. `usuario_premium`

Se inicia con:

\[
C_0=\{usuario\_id\}
\]

Aplicando las dependencias:

\[
C_1=\{usuario\_id,tipo\_usuario,metodo\_pago,fecha\_renovacion\}
\]

\[
usuario\_id^+=\{usuario\_id,tipo\_usuario,metodo\_pago,fecha\_renovacion\}
\]

**Clave candidata:** `{usuario_id}`.

### 8. `produccion_audiovisual`

Se inicia con:

\[
C_0=\{contenido\_id\}
\]

Aplicando las dependencias:

\[
C_1=\{contenido\_id,titulo,anio\_estreno,director,tipo\_produccion,playlist\_id\}
\]

\[
contenido\_id^+=\{contenido\_id,titulo,anio\_estreno,director,tipo\_produccion,playlist\_id\}
\]

**Clave candidata:** `{contenido_id}`.

### 9. `produccion_generos`

Cierres individuales:

\[
contenido\_id^+=\{contenido\_id\}
\]

\[
genero^+=\{genero\}
\]

Ninguno de los atributos por separado determina toda la relación.

Cierre de la combinación:

\[
(contenido\_id,genero)^+=\{contenido\_id,genero\}
\]

**Clave candidata:** `{contenido_id, genero}`.

### 10. `peliculas`

Se inicia con:

\[
C_0=\{contenido\_id\}
\]

Aplicando las dependencias:

\[
C_1=\{contenido\_id,tipo\_produccion,duracion\}
\]

\[
contenido\_id^+=\{contenido\_id,tipo\_produccion,duracion\}
\]

**Clave candidata:** `{contenido_id}`.

### 11. `pelicula_idiomas`

Cierres individuales:

\[
contenido\_id^+=\{contenido\_id\}
\]

\[
idioma^+=\{idioma\}
\]

Cierre de la combinación:

\[
(contenido\_id,idioma)^+=\{contenido\_id,idioma\}
\]

**Clave candidata:** `{contenido_id, idioma}`.

### 12. `series`

Se inicia con:

\[
C_0=\{contenido\_id\}
\]

Aplicando las dependencias:

\[
C_1=\{contenido\_id,tipo\_produccion,num\_temporadas,num\_capitulos\}
\]

\[
contenido\_id^+=\{contenido\_id,tipo\_produccion,num\_temporadas,num\_capitulos\}
\]

**Clave candidata:** `{contenido_id}`.

### 13. `resenas`

Se inicia con:

\[
C_0=\{resena\_id\}
\]

Aplicando las dependencias:

\[
C_1=\{resena\_id,puntuacion,comentario,fecha,usuario\_id,contenido\_id\}
\]

\[
resena\_id^+=\{resena\_id,puntuacion,comentario,fecha,usuario\_id,contenido\_id\}
\]

**Clave candidata:** `{resena_id}`.

### 14. `visualiza`

Cierres individuales:

\[
usuario\_id^+=\{usuario\_id\}
\]

\[
contenido\_id^+=\{contenido\_id\}
\]

Ninguno determina los datos restantes de visualización.

Cierre de la combinación:

\[
C_0=\{usuario\_id,contenido\_id\}
\]

\[
C_1=\{usuario\_id,contenido\_id,porcentaje\_avance,fecha\_reproduccion,estado\}
\]

\[
(usuario\_id,contenido\_id)^+=\{usuario\_id,contenido\_id,porcentaje\_avance,fecha\_reproduccion,estado\}
\]

**Clave candidata:** `{usuario_id, contenido_id}`.

### 15. `esta_basada_en`

Se inicia con:

\[
C_0=\{contenido\_id\}
\]

Aplicando las dependencias:

\[
C_1=\{contenido\_id,libro\_id,comic\_id\}
\]

\[
contenido\_id^+=\{contenido\_id,libro\_id,comic\_id\}
\]

**Clave candidata:** `{contenido_id}`.

### Resumen de claves candidatas

| Tabla | Clave o claves candidatas |
|---|---|
| playlist | identificador_id |
| autores | autor_id |
| libros | libro_id |
| comics | comic_id |
| usuarios | usuario_id, correo |
| usuario_estandar | usuario_id |
| usuario_premium | usuario_id |
| produccion_audiovisual | contenido_id |
| produccion_generos | (contenido_id, genero) |
| peliculas | contenido_id |
| pelicula_idiomas | (contenido_id, idioma) |
| series | contenido_id |
| resenas | resena_id |
| visualiza | (usuario_id, contenido_id) |
| esta_basada_en | contenido_id |

## 1.2.3. Cubierta mínima

La cubierta mínima es un conjunto equivalente al conjunto original de dependencias funcionales, pero expresado de manera simplificada.

Para obtenerla se separan los atributos del lado derecho, se comprueba que no existan atributos innecesarios en el lado izquierdo y se eliminan las dependencias redundantes.

### Paso 1. Lados derechos simples

Las dependencias se expresan con un solo atributo a la derecha. Por ejemplo:

\[
usuario\_id\rightarrow correo,fecha\_registro,nombre
\]

se separa en:

\[
usuario\_id\rightarrow correo
\]

\[
usuario\_id\rightarrow fecha\_registro
\]

\[
usuario\_id\rightarrow nombre
\]

Este procedimiento se aplica a las relaciones que tienen más de un atributo del lado derecho.

### Paso 2. Comprobación de atributos sobrantes en el lado izquierdo

En las tablas con determinante simple, el lado izquierdo contiene únicamente la clave primaria, por lo que no hay atributos que puedan eliminarse.

En `visualiza`, la clave es compuesta. Se comprueba que ambos atributos son necesarios:

\[
usuario\_id^+=\{usuario\_id\}
\]

\[
contenido\_id^+=\{contenido\_id\}
\]

Ninguno de los cierres individuales determina `porcentaje_avance`, `fecha_reproduccion` ni `estado`. Por ello, no se puede eliminar ninguno de los atributos de la combinación.

En `produccion_generos` y `pelicula_idiomas` tampoco se puede eliminar una parte de la clave compuesta, ya que ninguno de sus atributos determina al otro.

### Paso 3. Eliminación de dependencias redundantes

En `usuarios`, se conserva la dependencia:

\[
usuario\_id\rightarrow correo
\]

\[
correo\rightarrow usuario\_id
\]

La primera dependencia permite obtener el correo a partir del identificador y la segunda permite obtener el identificador a partir del correo.

No se incluyen dependencias adicionales desde `correo` hacia los demás atributos porque se pueden deducir por transitividad, pasando por `usuario_id`.

### Cubierta mínima resultante por tabla

**1. `playlist`**

\[
F_m=\{
identificador\_id\rightarrow nombre,
identificador\_id\rightarrow enlace
\}
\]

No se elimina ninguna dependencia porque cada una determina un atributo diferente.

**2. `autores`**

\[
F_m=\{autor\_id\rightarrow biografia\}
\]

No existen dependencias redundantes.

**3. `libros`**

\[
F_m=\{
libro\_id\rightarrow titulo,
libro\_id\rightarrow anio\_publicacion,
libro\_id\rightarrow autor\_id
\}
\]

No hay atributos sobrantes ni dependencias redundantes.

**4. `comics`**

\[
F_m=\{
comic\_id\rightarrow titulo,
comic\_id\rightarrow numero\_edicion,
comic\_id\rightarrow autor\_id
\}
\]

No hay atributos sobrantes ni dependencias redundantes.

**5. `usuarios`**

\[
\begin{aligned}
F_m=\{&
usuario\_id\rightarrow correo,\\
&usuario\_id\rightarrow fecha\_registro,\\
&usuario\_id\rightarrow nombre,\\
&usuario\_id\rightarrow apellidos,\\
&usuario\_id\rightarrow tipo\_usuario,\\
&usuario\_id\rightarrow activo,\\
&correo\rightarrow usuario\_id
\}
\end{aligned}
\]

Se conserva la dependencia de `usuario_id` hacia sus atributos y la dependencia de `correo` hacia `usuario_id`. Las dependencias desde `correo` hacia los demás atributos se deducen por transitividad y no se agregan a la cubierta mínima.

**6. `usuario_estandar`**

\[
F_m=\{
usuario\_id\rightarrow tipo\_usuario,
usuario\_id\rightarrow limite\_resenas,
usuario\_id\rightarrow publicidad
\}
\]

No hay atributos sobrantes ni dependencias redundantes.

**7. `usuario_premium`**

\[
F_m=\{
usuario\_id\rightarrow tipo\_usuario,
usuario\_id\rightarrow metodo\_pago,
usuario\_id\rightarrow fecha\_renovacion
\}
\]

No hay atributos sobrantes ni dependencias redundantes.

**8. `produccion_audiovisual`**

\[
\begin{aligned}
F_m=\{&
contenido\_id\rightarrow titulo,\\
&contenido\_id\rightarrow anio\_estreno,\\
&contenido\_id\rightarrow director,\\
&contenido\_id\rightarrow tipo\_produccion,\\
&contenido\_id\rightarrow playlist\_id
\}
\end{aligned}
\]

No hay atributos sobrantes ni dependencias redundantes.

**9. `produccion_generos`**

\[
F_m=\varnothing
\]

No existen dependencias funcionales no triviales entre sus atributos.

**10. `peliculas`**

\[
F_m=\{
contenido\_id\rightarrow tipo\_produccion,
contenido\_id\rightarrow duracion
\}
\]

No hay atributos sobrantes ni dependencias redundantes.

**11. `pelicula_idiomas`**

\[
F_m=\varnothing
\]

No existen dependencias funcionales no triviales entre sus atributos.

**12. `series`**

\[
F_m=\{
contenido\_id\rightarrow tipo\_produccion,
contenido\_id\rightarrow num\_temporadas,
contenido\_id\rightarrow num\_capitulos
\}
\]

No hay atributos sobrantes ni dependencias redundantes.

**13. `resenas`**

\[
\begin{aligned}
F_m=\{&
resena\_id\rightarrow puntuacion,\\
&resena\_id\rightarrow comentario,\\
&resena\_id\rightarrow fecha,\\
&resena\_id\rightarrow usuario\_id,\\
&resena\_id\rightarrow contenido\_id
\}
\end{aligned}
\]

No hay atributos sobrantes ni dependencias redundantes.

**14. `visualiza`**

\[
\begin{aligned}
F_m=\{&
(usuario\_id,contenido\_id)\rightarrow porcentaje\_avance,\\
&(usuario\_id,contenido\_id)\rightarrow fecha\_reproduccion,\\
&(usuario\_id,contenido\_id)\rightarrow estado
\}
\end{aligned}
\]

Ambos atributos del lado izquierdo son necesarios, como se comprobó mediante sus cierres individuales.

**15. `esta_basada_en`**

\[
F_m=\{
contenido\_id\rightarrow libro\_id,
contenido\_id\rightarrow comic\_id
\}
\]

No hay atributos sobrantes ni dependencias redundantes.

## 1.2.4. Intercambio de dependencias funcionales con otro equipo

Se intercambiará el conjunto de dependencias funcionales con otro equipo que trabaje en un dominio similar.

Para comprobar la equivalencia, se comparará el conjunto de nuestro proyecto, representado por F, con el conjunto recibido, representado por G.

Se deben comprobar las siguientes condiciones:

\[
F\models G
\]

\[
G\models F
\]

Esto significa que todas las dependencias de G deben poder deducirse de F y todas las dependencias de F deben poder deducirse de G.

La comprobación se realizará mediante el cálculo de cierres de los determinantes de las dependencias recibidas.

**Conjunto de dependencias del otro equipo:** Pendiente de recibir.

**Resultado de equivalencia:** Pendiente de realizar el intercambio y calcular los cierres.

### Conclusión del ejercicio 1.2

A partir de las reglas del negocio y las restricciones del esquema se identificaron las dependencias funcionales de las 15 relaciones. Los cierres permitieron encontrar las claves candidatas y comprobar la necesidad de las claves compuestas en las tablas de géneros, idiomas y visualización.

Finalmente, se obtuvo una cubierta mínima para cada relación, separando los atributos del lado derecho y comprobando que los determinantes compuestos fueran mínimos. La comparación con otro equipo queda pendiente hasta recibir su conjunto de dependencias funcionales.