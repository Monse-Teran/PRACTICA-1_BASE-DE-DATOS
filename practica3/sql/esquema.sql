-- =====================================================================
-- esquema.sql  |  Practica 3: transformacion EER -> relacional
-- Proyecto propio: plataforma de catalogo audiovisual y literario
-- Gestor objetivo: PostgreSQL (tipos y sintaxis estandar; tambien corre
-- sin cambios en SQLite con PRAGMA foreign_keys = ON)
-- Orden de creacion: primero las tablas que no dependen de otras.
-- =====================================================================

-- Regla 1: entidad fuerte PLAYLIST
CREATE TABLE playlist (
    identificador_id INTEGER      NOT NULL,
    nombre           VARCHAR(80)  NOT NULL,
    enlace           VARCHAR(255),
    CONSTRAINT pk_playlist PRIMARY KEY (identificador_id)
);

-- Regla 1: entidad fuerte AUTORES
CREATE TABLE autores (
    autor_id  INTEGER NOT NULL,
    biografia TEXT,
    CONSTRAINT pk_autores PRIMARY KEY (autor_id)
);

-- Regla 1 + Regla 4 (autores 1:N libros, minimo 1 del lado libro)
CREATE TABLE libros (
    libro_id         INTEGER      NOT NULL,
    titulo           VARCHAR(150) NOT NULL,
    anio_publicacion INTEGER,
    autor_id         INTEGER      NOT NULL,
    CONSTRAINT pk_libros PRIMARY KEY (libro_id),
    CONSTRAINT ck_libros_anio CHECK (anio_publicacion BETWEEN 1 AND 2100),
    CONSTRAINT fk_libros_autor FOREIGN KEY (autor_id)
        REFERENCES autores (autor_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- Regla 1 + Regla 4 (autores 1:N comics)
CREATE TABLE comics (
    comic_id         INTEGER      NOT NULL,
    titulo           VARCHAR(150) NOT NULL,
    numero_edicion   INTEGER,
    autor_id         INTEGER      NOT NULL,
    CONSTRAINT pk_comics PRIMARY KEY (comic_id),
    CONSTRAINT ck_comics_edicion CHECK (numero_edicion > 0),
    CONSTRAINT fk_comics_autor FOREIGN KEY (autor_id)
        REFERENCES autores (autor_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- Regla 1 + Regla 2 (nombre completo -> nombre, apellidos)
-- Regla 9, estrategia A: supertipo con discriminador tipo_usuario
-- (NULL = usuario general, porque la jerarquia es parcial)
CREATE TABLE usuarios (
    usuario_id     INTEGER      NOT NULL,
    correo         VARCHAR(120) NOT NULL,
    fecha_registro DATE         NOT NULL DEFAULT CURRENT_DATE,
    nombre         VARCHAR(60)  NOT NULL,
    apellidos      VARCHAR(100) NOT NULL,
    tipo_usuario   VARCHAR(10),
    CONSTRAINT pk_usuarios PRIMARY KEY (usuario_id),
    CONSTRAINT uq_usuarios_correo UNIQUE (correo),
    CONSTRAINT uq_usuarios_id_tipo UNIQUE (usuario_id, tipo_usuario),
    CONSTRAINT ck_usuarios_correo CHECK (correo LIKE '%@%'),
    CONSTRAINT ck_usuarios_tipo CHECK (tipo_usuario IN ('estandar', 'premium'))
);

-- Regla 9, estrategia A: subtipo USUARIO_ESTANDAR
CREATE TABLE usuario_estandar (
    usuario_id     INTEGER     NOT NULL,
    tipo_usuario   VARCHAR(10) NOT NULL DEFAULT 'estandar',
    limite_resenas INTEGER     NOT NULL,
    publicidad     BOOLEAN     NOT NULL DEFAULT TRUE,
    CONSTRAINT pk_usuario_estandar PRIMARY KEY (usuario_id),
    CONSTRAINT ck_usuario_estandar_tipo CHECK (tipo_usuario = 'estandar'),
    CONSTRAINT ck_usuario_estandar_limite CHECK (limite_resenas >= 0),
    CONSTRAINT fk_usuario_estandar_usuario FOREIGN KEY (usuario_id, tipo_usuario)
        REFERENCES usuarios (usuario_id, tipo_usuario)
        ON DELETE CASCADE
        ON UPDATE RESTRICT
);

-- Regla 9, estrategia A: subtipo USUARIO_PREMIUM
CREATE TABLE usuario_premium (
    usuario_id       INTEGER     NOT NULL,
    tipo_usuario     VARCHAR(10) NOT NULL DEFAULT 'premium',
    metodo_pago      VARCHAR(30) NOT NULL,
    fecha_renovacion DATE,
    CONSTRAINT pk_usuario_premium PRIMARY KEY (usuario_id),
    CONSTRAINT ck_usuario_premium_tipo CHECK (tipo_usuario = 'premium'),
    CONSTRAINT fk_usuario_premium_usuario FOREIGN KEY (usuario_id, tipo_usuario)
        REFERENCES usuarios (usuario_id, tipo_usuario)
        ON DELETE CASCADE
        ON UPDATE RESTRICT
);

-- Regla 1 + Regla 6 (tiene, 1:1 con PLAYLIST: la clave de la entidad
-- obligatoria, playlist, viaja a la opcional, produccion, como FK UNIQUE)
-- Regla 9, estrategia A: supertipo con discriminador tipo_produccion
CREATE TABLE produccion_audiovisual (
    contenido_id    INTEGER      NOT NULL,
    titulo          VARCHAR(150) NOT NULL,
    anio_estreno    INTEGER,
    director        VARCHAR(100),
    tipo_produccion VARCHAR(10),
    playlist_id     INTEGER,
    CONSTRAINT pk_produccion PRIMARY KEY (contenido_id),
    CONSTRAINT uq_produccion_id_tipo UNIQUE (contenido_id, tipo_produccion),
    CONSTRAINT uq_produccion_playlist UNIQUE (playlist_id),
    CONSTRAINT ck_produccion_anio CHECK (anio_estreno BETWEEN 1888 AND 2100),
    CONSTRAINT ck_produccion_tipo CHECK (tipo_produccion IN ('pelicula', 'serie')),
    CONSTRAINT fk_produccion_playlist FOREIGN KEY (playlist_id)
        REFERENCES playlist (identificador_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Regla 3: atributo multivaluado generos
CREATE TABLE produccion_generos (
    contenido_id INTEGER     NOT NULL,
    genero       VARCHAR(40) NOT NULL,
    CONSTRAINT pk_produccion_generos PRIMARY KEY (contenido_id, genero),
    CONSTRAINT fk_generos_produccion FOREIGN KEY (contenido_id)
        REFERENCES produccion_audiovisual (contenido_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Regla 9, estrategia A: subtipo PELICULAS
CREATE TABLE peliculas (
    contenido_id    INTEGER     NOT NULL,
    tipo_produccion VARCHAR(10) NOT NULL DEFAULT 'pelicula',
    duracion        INTEGER,
    CONSTRAINT pk_peliculas PRIMARY KEY (contenido_id),
    CONSTRAINT ck_peliculas_tipo CHECK (tipo_produccion = 'pelicula'),
    CONSTRAINT ck_peliculas_duracion CHECK (duracion > 0),
    CONSTRAINT fk_peliculas_produccion FOREIGN KEY (contenido_id, tipo_produccion)
        REFERENCES produccion_audiovisual (contenido_id, tipo_produccion)
        ON DELETE CASCADE
        ON UPDATE RESTRICT
);

-- Regla 3: atributo multivaluado idiomas_audio de PELICULAS
CREATE TABLE pelicula_idiomas (
    contenido_id INTEGER     NOT NULL,
    idioma       VARCHAR(40) NOT NULL,
    CONSTRAINT pk_pelicula_idiomas PRIMARY KEY (contenido_id, idioma),
    CONSTRAINT fk_idiomas_pelicula FOREIGN KEY (contenido_id)
        REFERENCES peliculas (contenido_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Regla 9, estrategia A: subtipo SERIES
CREATE TABLE series (
    contenido_id    INTEGER     NOT NULL,
    tipo_produccion VARCHAR(10) NOT NULL DEFAULT 'serie',
    num_temporadas  INTEGER,
    num_capitulos   INTEGER,
    CONSTRAINT pk_series PRIMARY KEY (contenido_id),
    CONSTRAINT ck_series_tipo CHECK (tipo_produccion = 'serie'),
    CONSTRAINT ck_series_temporadas CHECK (num_temporadas > 0),
    CONSTRAINT ck_series_capitulos CHECK (num_capitulos > 0),
    CONSTRAINT fk_series_produccion FOREIGN KEY (contenido_id, tipo_produccion)
        REFERENCES produccion_audiovisual (contenido_id, tipo_produccion)
        ON DELETE CASCADE
        ON UPDATE RESTRICT
);

-- Regla 1 + Regla 4 aplicada dos veces:
--   escribe: usuarios (0,N) - resenas (1,1)  -> usuario_id NOT NULL
--   recibe:  produccion (0,N) - resenas (1,1) -> contenido_id NOT NULL
CREATE TABLE resenas (
    resena_id    INTEGER NOT NULL,
    puntuacion   INTEGER NOT NULL,
    comentario   TEXT,
    fecha        DATE    NOT NULL DEFAULT CURRENT_DATE,
    usuario_id   INTEGER NOT NULL,
    contenido_id INTEGER NOT NULL,
    CONSTRAINT pk_resenas PRIMARY KEY (resena_id),
    CONSTRAINT ck_resenas_puntuacion CHECK (puntuacion BETWEEN 1 AND 5),
    CONSTRAINT fk_resenas_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios (usuario_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_resenas_produccion FOREIGN KEY (contenido_id)
        REFERENCES produccion_audiovisual (contenido_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Regla 5: visualiza, relacion M:N con atributos propios
CREATE TABLE visualiza (
    usuario_id        INTEGER      NOT NULL,
    contenido_id      INTEGER      NOT NULL,
    porcentaje_avance DECIMAL(5,2) NOT NULL DEFAULT 0,
    fecha_reproduccion TIMESTAMP   NOT NULL,
    estado            VARCHAR(10)  NOT NULL,
    CONSTRAINT pk_visualiza PRIMARY KEY (usuario_id, contenido_id),
    CONSTRAINT ck_visualiza_avance CHECK (porcentaje_avance BETWEEN 0 AND 100),
    CONSTRAINT ck_visualiza_estado CHECK (estado IN ('pausado', 'terminado')),
    CONSTRAINT fk_visualiza_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios (usuario_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_visualiza_produccion FOREIGN KEY (contenido_id)
        REFERENCES produccion_audiovisual (contenido_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Regla 7: relacion ternaria esta_basada_en
-- (produccion (0,1), libros (0,N), comics (0,N)); como la produccion
-- participa como maximo una vez, su clave es la clave primaria de la tabla.
CREATE TABLE esta_basada_en (
    contenido_id INTEGER NOT NULL,
    libro_id     INTEGER,
    comic_id     INTEGER,
    CONSTRAINT pk_esta_basada_en PRIMARY KEY (contenido_id),
    CONSTRAINT ck_basada_en_origen CHECK (libro_id IS NOT NULL OR comic_id IS NOT NULL),
    CONSTRAINT fk_basada_produccion FOREIGN KEY (contenido_id)
        REFERENCES produccion_audiovisual (contenido_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_basada_libro FOREIGN KEY (libro_id)
        REFERENCES libros (libro_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_basada_comic FOREIGN KEY (comic_id)
        REFERENCES comics (comic_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
