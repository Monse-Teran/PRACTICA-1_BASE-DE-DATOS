# Práctica 4. Dominios y restricciones

## 1.1 Definición de dominios y tipos de datos

En este apartado se documentan los tipos de datos utilizados en las tablas del proyecto propio, indicando su longitud o precisión cuando corresponde y justificando su elección de acuerdo con la información que almacena cada columna.

### Tabla autores

| Columna | Tipo de dato | Longitud/precisión | Justificación |
|---|---|---|---|
| autor_id | INTEGER | 32 bits | Identifica de manera única a cada autor mediante un valor entero. |
| biografia | TEXT | Variable | Permite almacenar biografías de longitud variable sin establecer un límite fijo. |

### Tabla comics

| Columna | Tipo de dato | Longitud/precisión | Justificación |
|---|---|---|---|
| comic_id | INTEGER | 32 bits | Identificador entero para cada cómic. |
| titulo | VARCHAR(150) | 150 caracteres | Almacena el título del cómic con una longitud máxima definida. |
| numero_edicion | INTEGER | 32 bits | Representa el número de edición mediante un valor entero. |
| autor_id | INTEGER | 32 bits | Almacena el identificador del autor relacionado con el cómic. |

### Tabla esta_basada_en

| Columna | Tipo de dato | Longitud/precisión | Justificación |
|---|---|---|---|
| contenido_id | INTEGER | 32 bits | Identifica la producción audiovisual relacionada. |
| libro_id | INTEGER | 32 bits | Almacena el identificador del libro relacionado, cuando existe. |
| comic_id | INTEGER | 32 bits | Almacena el identificador del cómic relacionado, cuando existe. |

### Tabla libros

| Columna | Tipo de dato | Longitud/precisión | Justificación |
|---|---|---|---|
| libro_id | INTEGER | 32 bits | Identificador entero para cada libro. |
| titulo | VARCHAR(150) | 150 caracteres | Almacena el título del libro con una longitud máxima definida. |
| anio_publicacion | INTEGER | 32 bits | Representa el año de publicación mediante un número entero. |
| autor_id | INTEGER | 32 bits | Almacena el identificador del autor relacionado con el libro. |

### Tabla pelicula_idiomas

| Columna | Tipo de dato | Longitud/precisión | Justificación |
|---|---|---|---|
| contenido_id | INTEGER | 32 bits | Identifica la producción audiovisual a la que pertenece el idioma. |
| idioma | VARCHAR(40) | 40 caracteres | Almacena el nombre del idioma con una longitud máxima definida. |

### Tabla peliculas

| Columna | Tipo de dato | Longitud/precisión | Justificación |
|---|---|---|---|
| contenido_id | INTEGER | 32 bits | Identificador de la producción audiovisual correspondiente a la película. |
| tipo_produccion | VARCHAR(10) | 10 caracteres | Almacena el tipo de producción, en este caso película. |
| duracion | INTEGER | 32 bits | Representa la duración de la película mediante un número entero. |

### Tabla playlist

| Columna | Tipo de dato | Longitud/precisión | Justificación |
|---|---|---|---|
| identificador_id | INTEGER | 32 bits | Identificador entero de cada lista de reproducción. |
| nombre | VARCHAR(80) | 80 caracteres | Almacena el nombre de la lista con un máximo de 80 caracteres. |
| enlace | VARCHAR(255) | 255 caracteres | Permite almacenar enlaces con una longitud máxima de 255 caracteres. |

### Tabla produccion_audiovisual

| Columna | Tipo de dato | Longitud/precisión | Justificación |
|---|---|---|---|
| contenido_id | INTEGER | 32 bits | Identificador entero de cada producción audiovisual. |
| titulo | VARCHAR(150) | 150 caracteres | Almacena el título de la producción con un máximo de 150 caracteres. |
| anio_estreno | INTEGER | 32 bits | Representa el año de estreno mediante un número entero. |
| director | VARCHAR(100) | 100 caracteres | Almacena el nombre del director con un máximo de 100 caracteres. |
| tipo_produccion | VARCHAR(10) | 10 caracteres | Identifica el tipo de producción, por ejemplo, película o serie. |
| playlist_id | INTEGER | 32 bits | Almacena el identificador de la lista de reproducción relacionada. |

### Tabla produccion_generos

| Columna | Tipo de dato | Longitud/precisión | Justificación |
|---|---|---|---|
| contenido_id | INTEGER | 32 bits | Identifica la producción audiovisual a la que pertenece el género. |
| genero | VARCHAR(40) | 40 caracteres | Almacena el nombre del género con un máximo de 40 caracteres. |

### Tabla resenas

| Columna | Tipo de dato | Longitud/precisión | Justificación |
|---|---|---|---|
| resena_id | INTEGER | 32