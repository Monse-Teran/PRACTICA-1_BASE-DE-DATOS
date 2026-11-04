-- =====================================================================
-- pruebas-de-restricciones.sql
-- Parte 1: datos validos (deben insertarse sin error)
-- Parte 2: INSERT que el gestor debe RECHAZAR (cada uno indica la
--          restriccion que viola)
-- =====================================================================

-- ---------- Parte 1: datos validos ----------
INSERT INTO playlist VALUES (1, 'Maraton de ciencia ficcion', 'https://ejemplo.mx/pl/1');
INSERT INTO autores  VALUES (1, 'Autor de ejemplo');
INSERT INTO libros   VALUES (1, 'Novela base', 1999, 1);
INSERT INTO comics   VALUES (1, 'Cronicas ilustradas', 3, 1);

INSERT INTO usuarios (usuario_id, correo, nombre, apellidos, tipo_usuario)
    VALUES (1, 'ana@correo.mx', 'Ana', 'Lopez Perez', 'estandar');
INSERT INTO usuarios (usuario_id, correo, nombre, apellidos, tipo_usuario)
    VALUES (2, 'luis@correo.mx', 'Luis', 'Garcia Ruiz', 'premium');
INSERT INTO usuarios (usuario_id, correo, nombre, apellidos)
    VALUES (3, 'eva@correo.mx', 'Eva', 'Mora Diaz');
INSERT INTO usuario_estandar (usuario_id, limite_resenas) VALUES (1, 10);
INSERT INTO usuario_premium (usuario_id, metodo_pago, fecha_renovacion)
    VALUES (2, 'tarjeta', '2026-12-01');

INSERT INTO produccion_audiovisual (contenido_id, titulo, anio_estreno, director, tipo_produccion, playlist_id)
    VALUES (10, 'Pelicula de prueba', 2020, 'Directora X', 'pelicula', 1);
INSERT INTO produccion_audiovisual (contenido_id, titulo, anio_estreno, director, tipo_produccion)
    VALUES (20, 'Serie de prueba', 2022, 'Director Y', 'serie');
INSERT INTO peliculas (contenido_id, duracion) VALUES (10, 120);
INSERT INTO series (contenido_id, num_temporadas, num_capitulos) VALUES (20, 2, 16);
INSERT INTO produccion_generos VALUES (10, 'Ciencia ficcion');
INSERT INTO produccion_generos VALUES (10, 'Accion');
INSERT INTO pelicula_idiomas VALUES (10, 'Espanol');
INSERT INTO pelicula_idiomas VALUES (10, 'Ingles');

INSERT INTO resenas (resena_id, puntuacion, comentario, usuario_id, contenido_id)
    VALUES (1, 5, 'Muy buena', 1, 10);
INSERT INTO visualiza VALUES (1, 10, 45.50, '2026-10-01 20:30:00', 'pausado');
INSERT INTO esta_basada_en VALUES (10, 1, NULL);

-- ---------- Parte 2: INSERT que deben fallar ----------
-- Prueba 1 (UNIQUE): correo repetido
INSERT INTO usuarios (usuario_id, correo, nombre, apellidos)
    VALUES (4, 'ana@correo.mx', 'Otra', 'Persona');

-- Prueba 2 (NOT NULL): usuario sin correo
INSERT INTO usuarios (usuario_id, correo, nombre, apellidos)
    VALUES (5, NULL, 'Sin', 'Correo');

-- Prueba 3 (CHECK): puntuacion fuera del rango 1-5
INSERT INTO resenas (resena_id, puntuacion, usuario_id, contenido_id)
    VALUES (2, 9, 1, 10);

-- Prueba 4 (FK): resena de un usuario que no existe
INSERT INTO resenas (resena_id, puntuacion, usuario_id, contenido_id)
    VALUES (3, 4, 999, 10);

-- Prueba 5 (CHECK): estado distinto de pausado / terminado
INSERT INTO visualiza VALUES (2, 20, 10, '2026-10-02 21:00:00', 'abandonado');

-- Prueba 6 (disyuncion, FK compuesta): el usuario 2 es premium y se
-- intenta registrar tambien como estandar
INSERT INTO usuario_estandar (usuario_id, limite_resenas) VALUES (2, 5);

-- Prueba 7 (CHECK): esta_basada_en sin libro ni comic
INSERT INTO esta_basada_en VALUES (20, NULL, NULL);

-- Prueba 8 (UNIQUE, relacion 1:1 tiene): la misma playlist en dos producciones
INSERT INTO produccion_audiovisual (contenido_id, titulo, tipo_produccion, playlist_id)
    VALUES (30, 'Otra pelicula', 'pelicula', 1);

