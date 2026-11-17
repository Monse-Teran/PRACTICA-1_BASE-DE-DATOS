# Fuente de Datos del Proyecto (`fuente.md`)

## 1. Referencia y Licencia

* **Referencia (APA 7.ª edición):**
  Bansal, S. (2021). *Netflix Movies and TV Shows* (Versión 5) [Conjunto de datos]. Kaggle. Consultado el 17 de noviembre de 2026, de https://www.kaggle.com/datasets/shivamb/netflix-shows

* **Licencia y permisos de uso:**
  **CC0 1.0 Universal (Public Domain Dedication)**. Esta licencia permite copiar, modificar, distribuir, transformar y utilizar el conjunto de datos de forma libre para fines académicos, de investigación o comerciales sin necesidad de solicitar autorización previa.

* **Justificación de datos sintéticos complementarios:**
  Antes de generar datos mediante código, se realizó una búsqueda exhaustiva en repositorios abiertos (*Kaggle*, *IMDb Non-Commercial Datasets*, *MovieLens / GroupLens* y *Datos Abiertos México*) utilizando términos como `"streaming user watch history"`, `"platform user subscriptions reviews"` y `"movie book comic adaptations"`. Se concluyó que no existe un conjunto de datos público que contenga simultáneamente cuentas de usuarios de una plataforma de streaming con niveles estándar/premium, historial de reproducción (`visualiza`), listas de reproducción personalizadas (`playlist`), reseñas y obras literarias de origen (`autores`, `libros`, `comics`, `esta_basada_en`).
  Por lo tanto, el catálogo audiovisual principal se poblará con el conjunto real citado, mientras que las entidades operativas de usuarios, comunidad y adaptaciones literarias se generarán mediante un script en Python (`Faker`) respetando todas las restricciones del esquema (`CHECK`, `UNIQUE`, llaves foráneas) y asegurando al menos **200 registros por tabla principal**.

---

## 2. Características del Conjunto de Datos Original

* **Nombre del archivo:** `netflix_titles.csv`
* **Formato original:** CSV (valores separados por comas), codificación `UTF-8`.
* **Tamaño en disco:** 3,319.99 KB (~3.24 MB).
* **Cantidad de registros:** 8,807 filas (sin contar el encabezado).
* **Campos originales (12 columnas):**
  1. `show_id`
  2. `type`
  3. `title`
  4. `director`
  5. `cast`
  6. `country`
  7. `date_added`
  8. `release_year`
  9. `rating`
  10. `duration`
  11. `listed_in`
  12. `description`

---

## 3. Tabla de Correspondencia con el Esquema (`esquema.sql`)

| Campo en CSV original | Tabla destino | Columna destino | Transformación / Justificación (si no se usa) |
| :--- | :--- | :--- | :--- |
| `show_id` | *No se usa* | *N/A* | Se descarta el identificador alfanumérico (`s1`, `s2`...); se asigna un `contenido_id` entero secuencial (`INTEGER`). |
| `type` | `produccion_audiovisual` | `tipo_produccion` | Se normaliza `'Movie'` $\rightarrow$ `'pelicula'` y `'TV Show'` $\rightarrow$ `'serie'` para cumplir `ck_produccion_tipo`. |
| `title` | `produccion_audiovisual` | `titulo` | Se eliminan espacios sobrantes (`trim`); todos los valores cumplen el límite `VARCHAR(150)`. |
| `release_year` | `produccion_audiovisual` | `anio_estreno` | Se convierte a `INTEGER` validando el rango `1888–2100` (`ck_produccion_anio`). |
| `director` | `produccion_audiovisual` | `director` | Cadenas vacías se convierten en `NULL`; valores mayores a 100 caracteres se truncan a `VARCHAR(100)`. |
| `listed_in` | `produccion_generos` | `genero` | Atributo multivaluado: se divide por comas (`,`) para insertar una tupla por cada género asociado al `contenido_id`. |
| `duration` (si `type = 'Movie'`) | `peliculas` | `duracion` | Se extrae el valor numérico entero eliminando el sufijo `" min"` (`ck_peliculas_duracion`). |
| `duration` (si `type = 'TV Show'`) | `series` | `num_temporadas` | Se extrae el valor numérico entero eliminando `" Season"` / `" Seasons"` (`ck_series_temporadas`). |
| `country` | `pelicula_idiomas` | `idioma` | Para registros de tipo `'pelicula'`, se toma el primer país listado y se mapea a su idioma principal (ej. *United States* $\rightarrow$ `'Inglés'`, *Mexico* $\rightarrow$ `'Español'`). |
| `cast` | *No se usa* | *N/A* | El esquema relacional actual no modela una entidad para actores o reparto. |
| `date_added` | *No se usa* | *N/A* | Fecha de incorporación al catálogo comercial de Netflix; no forma parte de los atributos de `produccion_audiovisual`. |
| `rating` | *No se usa* | *N/A* | Clasificación por edades no contemplada en el modelo EER/relacional del proyecto. |
| `description` | *No se usa* | *N/A* | Sinopsis textual excluida del esquema de la base de datos. |

---

## 4. Problemas de Calidad Detectados y Decisiones de Limpieza

1. **Valores vacíos (`NULL`) en `director` (2,634 registros) y `country` (831 registros):**
   * *Problema:* Aparecen como cadenas vacías (`""`) en el CSV.
   * *Decisión:* En `produccion_audiovisual.director` se transforman a `NULL` explícito, ya que la columna no tiene restricción `NOT NULL`. En `pelicula_idiomas.idioma`, cuando `country` está vacío se asigna `'No especificado'` para preservar la integridad de la llave primaria compuesta `(contenido_id, idioma)`.
2. **Longitud excesiva en `director` (14 registros > 100 caracteres):**
   * *Problema:* Producciones codirigidas por múltiples personas superan los 100 caracteres, lo que provocaría un error de truncamiento (`StringDataRightTruncation`) en `VARCHAR(100)`.
   * *Decisión:* Se conserva el primer director principal (separando por coma) o se trunca a 100 caracteres durante la etapa de limpieza previa a la carga.
3. **Formato mixto en `duration` y valores faltantes:**
   * *Problema:* La misma columna mezcla unidades distintas (`"90 min"` vs `"2 Seasons"`) y presenta 3 registros sin duración definida.
   * *Decisión:* Se separa la lógica según `tipo_produccion`: las películas van a `peliculas(duracion)` y las series a `series(num_temporadas)`. Si un registro carece de duración válida (`<= 0` o vacío), su duración se carga como `NULL` para cumplir con `CHECK (duracion > 0)`.
4. **Atributos multivaluados en una sola celda (`listed_in`):**
   * *Problema:* Los géneros vienen concatenados en una cadena separada por comas (ej. `"Dramas, Independent Movies"`).
   * *Decisión:* Se normalizan en Python separando por `,` y eliminando espacios laterales antes de poblar la tabla `produccion_generos`.
5. **Duplicados:**
   * *Problema:* Posible repetición de títulos en el catálogo.
   * *Decisión:* Se verificó la unicidad de la combinación `(title, release_year)` encontrando **0 registros duplicados**.
   * 
