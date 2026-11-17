import csv
import io
import os
import random
import time
from datetime import timedelta
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from faker import Faker

# Cargar variables de entorno desde .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

RUTA_CSV = BASE_DIR / "datos" / "netflix_titles.csv"

# Semilla fija para reproducibilidad e idempotencia
SEMILLA = 42
random.seed(SEMILLA)
fake = Faker("es_MX")
Faker.seed(SEMILLA)


def obtener_conexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "practica3_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )


def limpiar_valor(valor):
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto if texto != "" else None


def obtener_limites_varchar(cur):
    """Consulta el limite exacto VARCHAR(n) de todas las columnas de la BD."""
    cur.execute(
        """
        SELECT table_name, column_name, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = 'public' AND character_maximum_length IS NOT NULL;
        """
    )
    return {(t, c): max_len for t, c, max_len in cur.fetchall()}


def ejecutar_copy_idempotente(cur, tabla, columnas, filas, limites):
    """
    Carga masiva en memoria usando PostgreSQL COPY hacia una tabla temporal
    ajustando longitudes VARCHAR automaticamente e insertando con ON CONFLICT DO NOTHING
    (cubre tanto PRIMARY KEY como restricciones UNIQUE secundarias).
    """
    if not filas:
        return 0, 0

    max_lens = [limites.get((tabla, col)) for col in columnas]
    filas_ajustadas = []
    for fila in filas:
        nueva = []
        for val, mlen in zip(fila, max_lens):
            if val is not None and mlen is not None and isinstance(val, str) and len(val) > mlen:
                nueva.append(val[:mlen])
            else:
                nueva.append(val)
        filas_ajustadas.append(nueva)

    temp_table = f"tmp_{tabla}_{random.randint(1000, 99999)}"
    cols_str = ", ".join(columnas)

    cur.execute(
        f"CREATE TEMP TABLE {temp_table} (LIKE {tabla} INCLUDING DEFAULTS) ON COMMIT DROP;"
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter="\t", lineterminator="\n")
    for fila in filas_ajustadas:
        writer.writerow(["\\N" if v is None else v for v in fila])
    buffer.seek(0)

    cur.copy_expert(
        f"COPY {temp_table} ({cols_str}) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t', NULL '\\N')",
        buffer,
    )

    cur.execute(
        f"""
        INSERT INTO {tabla} ({cols_str})
        SELECT {cols_str} FROM {temp_table}
        ON CONFLICT DO NOTHING;
        """
    )
    insertados = cur.rowcount
    omitidos = len(filas_ajustadas) - insertados
    return insertados, omitidos


def medir_inserts_individuales(cur, filas_prueba):
    """Mide el tiempo equivalente de 1,000 INSERT individuales para comparar contra COPY."""
    cur.execute(
        """
        CREATE TEMP TABLE tmp_benchmark_insert (
            id INT PRIMARY KEY,
            titulo VARCHAR(255),
            anio INT
        ) ON COMMIT DROP;
        """
    )
    t0 = time.perf_counter()
    for idx, titulo, anio in filas_prueba:
        cur.execute(
            "INSERT INTO tmp_benchmark_insert (id, titulo, anio) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
            (idx, titulo, anio),
        )
    return time.perf_counter() - t0


def preparar_datos_csv(offset_id=100):
    producciones = []
    peliculas = []
    series = []
    generos_rel = set()
    idiomas_pelicula = set()

    with open(RUTA_CSV, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for raw_idx, row in enumerate(reader, start=1):
            idx = raw_idx + offset_id
            tipo_raw = limpiar_valor(row.get("type"))
            titulo = limpiar_valor(row.get("title"))
            if not titulo or tipo_raw not in ("Movie", "TV Show"):
                continue

            tipo_prod = "pelicula" if tipo_raw == "Movie" else "serie"
            director = limpiar_valor(row.get("director"))

            try:
                anio_estreno = int(limpiar_valor(row.get("release_year")))
            except (TypeError, ValueError):
                anio_estreno = 2020

            playlist_id = idx
            duracion_raw = limpiar_valor(row.get("duration")) or ""

            producciones.append(
                (idx, titulo, anio_estreno, director, tipo_prod, playlist_id)
            )

            if tipo_prod == "pelicula":
                minutos = 90
                if "min" in duracion_raw:
                    try:
                        minutos = int(duracion_raw.split()[0])
                    except ValueError:
                        minutos = 90
                peliculas.append((idx, tipo_prod, minutos))

                country_raw = limpiar_valor(row.get("country")) or "United States"
                idioma = (
                    "Espanol"
                    if any(p in country_raw for p in ("Mexico", "Spain", "Argentina", "Colombia", "Chile"))
                    else "Ingles"
                )
                idiomas_pelicula.add((idx, idioma))
                if idx % 4 == 0:
                    idiomas_pelicula.add((idx, "Subtitulado Espanol"))
            else:
                temporadas = 1
                if "Season" in duracion_raw:
                    try:
                        temporadas = int(duracion_raw.split()[0])
                    except ValueError:
                        temporadas = 1
                num_capitulos = temporadas * random.randint(6, 12)
                series.append((idx, tipo_prod, temporadas, num_capitulos))

            listed_in = limpiar_valor(row.get("listed_in"))
            if listed_in:
                for g in [x.strip() for x in listed_in.split(",") if x.strip()]:
                    generos_rel.add((idx, g))

    return {
        "producciones": producciones,
        "peliculas": peliculas,
        "series": series,
        "generos": sorted(generos_rel),
        "idiomas": sorted(idiomas_pelicula),
    }


def generar_datos_sinteticos_complementarios(producciones_csv, offset_id=100):
    playlists = []
    for p in producciones_csv:
        pid = p[5]
        nombre = f"Playlist - {p[1]}"[:80]
        enlace = f"https://cineclub.local/playlist/{pid}"
        playlists.append((pid, nombre, enlace))

    autores = []
    for i in range(1, 301):
        aid = i + offset_id
        biografia = f"{fake.name()}: {fake.sentence(nb_words=14)}"
        autores.append((aid, biografia))

    libros = []
    for i in range(1, 401):
        lid = i + offset_id
        titulo = f"{fake.catch_phrase()}"
        anio_pub = random.randint(1950, 2024)
        autor_id = random.randint(1, 300) + offset_id
        libros.append((lid, titulo, anio_pub, autor_id))

    comics = []
    for i in range(1, 301):
        cid = i + offset_id
        titulo = f"Serie Grafica {fake.word().capitalize()}"
        num_edicion = random.randint(1, 50)
        autor_id = random.randint(1, 300) + offset_id
        comics.append((cid, titulo, num_edicion, autor_id))

    basada_en = []
    contenidos_sample = random.sample(
        [p[0] for p in producciones_csv], k=min(500, len(producciones_csv))
    )
    for idx, cont_id in enumerate(contenidos_sample, start=1):
        if idx % 2 == 0:
            basada_en.append((cont_id, random.randint(1, 400) + offset_id, None))
        else:
            basada_en.append((cont_id, None, random.randint(1, 300) + offset_id))

    usuarios = []
    estandar = []
    premium = []
    correos_usados = set()
    metodos = ["Tarjeta Credito", "Tarjeta Debito", "PayPal", "Transferencia"]

    for i in range(1, 2501):
        uid = i + offset_id
        nombre = fake.first_name()
        apellidos = f"{fake.last_name()} {fake.last_name()}"
        correo = f"{fake.user_name()}_{uid}@{fake.free_email_domain()}"
        while correo in correos_usados:
            correo = f"{fake.user_name()}_{uid}_{random.randint(1,999)}@{fake.free_email_domain()}"
        correos_usados.add(correo)

        fecha_reg = fake.date_between(start_date="-4y", end_date="-10d")
        tipo_u = "premium" if i % 3 == 0 else "estandar"

        usuarios.append((uid, correo, fecha_reg, nombre, apellidos, tipo_u))
        if tipo_u == "estandar":
            estandar.append((uid, tipo_u, 5, True))
        else:
            fecha_ren = fecha_reg + timedelta(days=365)
            premium.append((uid, tipo_u, random.choice(metodos), fecha_ren))

    return {
        "playlists": playlists,
        "autores": autores,
        "libros": libros,
        "comics": comics,
        "basada_en": basada_en,
        "usuarios": usuarios,
        "estandar": estandar,
        "premium": premium,
    }


def generar_interacciones(usuarios_validos, contenidos_validos, offset_id=100):
    resenas = []
    visualizaciones = []
    uids = [u[0] for u in usuarios_validos]

    if not uids or not contenidos_validos:
        return resenas, visualizaciones

    pares_resena = set()
    rid = 1 + offset_id
    intentos = 0
    while len(resenas) < 4500 and intentos < 30000:
        intentos += 1
        uid = random.choice(uids)
        cid = random.choice(contenidos_validos)
        if (uid, cid) in pares_resena:
            continue
        pares_resena.add((uid, cid))
        puntuacion = random.randint(1, 5)
        comentario = fake.sentence(nb_words=12)
        fecha = fake.date_between(start_date="-2y", end_date="today")
        resenas.append((rid, puntuacion, comentario, fecha, uid, cid))
        rid += 1

    pares_vis = set()
    intentos_v = 0
    while len(visualizaciones) < 12000 and intentos_v < 60000:
        intentos_v += 1
        uid = random.choice(uids)
        cid = random.choice(contenidos_validos)
        if (uid, cid) in pares_vis:
            continue
        pares_vis.add((uid, cid))
        avance = round(random.uniform(5.0, 100.0), 2)
        fecha_rep = fake.date_time_between(start_date="-2y", end_date="now")
        estado = "terminado" if avance >= 90.0 else "pausado"
        visualizaciones.append((uid, cid, avance, fecha_rep, estado))

    return resenas, visualizaciones


def sincronizar_secuencias(cur):
    secuencias = [
        ("playlist", "identificador_id"),
        ("autores", "autor_id"),
        ("libros", "libro_id"),
        ("comics", "comic_id"),
        ("produccion_audiovisual", "contenido_id"),
        ("usuarios", "usuario_id"),
        ("resenas", "resena_id"),
    ]
    for tabla, col in secuencias:
        cur.execute(
            f"""
            SELECT setval(
                pg_get_serial_sequence('{tabla}', '{col}'),
                COALESCE((SELECT MAX({col}) FROM {tabla}), 1),
                true
            );
            """
        )


def main():
    print("=== INICIANDO CARGA MASIVA DE BASE DE DATOS (EJERCICIO 1.4) ===")
    t_inicio_total = time.perf_counter()

    # Desplazamiento fijo para convivir sin colision con registros iniciales de Practica 3
    OFFSET = 100
    datos_csv = preparar_datos_csv(offset_id=OFFSET)
    sint = generar_datos_sinteticos_complementarios(datos_csv["producciones"], offset_id=OFFSET)

    conn = obtener_conexion()
    try:
        with conn:
            with conn.cursor() as cur:
                limites = obtener_limites_varchar(cur)

                muestra_benchmark = [
                    (p[0], p[1][:255], p[2]) for p in datos_csv["producciones"][:1000]
                ]
                t_insert_1000 = medir_inserts_individuales(cur, muestra_benchmark)

                resumen = []

                for tabla, cols, filas in [
                    ("playlist", ["identificador_id", "nombre", "enlace"], sint["playlists"]),
                    ("autores", ["autor_id", "biografia"], sint["autores"]),
                ]:
                    t0 = time.perf_counter()
                    ins, omi = ejecutar_copy_idempotente(cur, tabla, cols, filas, limites)
                    resumen.append((tabla, ins, omi, time.perf_counter() - t0))

                cur.execute("SELECT autor_id FROM autores;")
                autores_ok = {r[0] for r in cur.fetchall()}

                libros_ok = [f for f in sint["libros"] if f[3] in autores_ok]
                comics_ok = [f for f in sint["comics"] if f[3] in autores_ok]

                for tabla, cols, filas in [
                    ("libros", ["libro_id", "titulo", "anio_publicacion", "autor_id"], libros_ok),
                    ("comics", ["comic_id", "titulo", "numero_edicion", "autor_id"], comics_ok),
                ]:
                    t0 = time.perf_counter()
                    ins, omi = ejecutar_copy_idempotente(cur, tabla, cols, filas, limites)
                    resumen.append((tabla, ins, omi, time.perf_counter() - t0))

                cur.execute("SELECT identificador_id FROM playlist;")
                playlists_ok = {r[0] for r in cur.fetchall()}
                prods_ok = [f for f in datos_csv["producciones"] if f[5] in playlists_ok]

                t0 = time.perf_counter()
                ins, omi = ejecutar_copy_idempotente(
                    cur,
                    "produccion_audiovisual",
                    ["contenido_id", "titulo", "anio_estreno", "director", "tipo_produccion", "playlist_id"],
                    prods_ok,
                    limites,
                )
                t_copy_prods = time.perf_counter() - t0
                resumen.append(("produccion_audiovisual", ins, omi, t_copy_prods))

                cur.execute("SELECT contenido_id, tipo_produccion FROM produccion_audiovisual;")
                prods_db = dict(cur.fetchall())
                contenidos_ids_ok = list(prods_db.keys())

                peliculas_ok = [f for f in datos_csv["peliculas"] if prods_db.get(f[0]) == "pelicula"]
                series_ok = [f for f in datos_csv["series"] if prods_db.get(f[0]) == "serie"]
                generos_ok = [f for f in datos_csv["generos"] if f[0] in prods_db]

                for tabla, cols, filas in [
                    ("peliculas", ["contenido_id", "tipo_produccion", "duracion"], peliculas_ok),
                    ("series", ["contenido_id", "tipo_produccion", "num_temporadas", "num_capitulos"], series_ok),
                    ("produccion_generos", ["contenido_id", "genero"], generos_ok),
                ]:
                    t0 = time.perf_counter()
                    ins, omi = ejecutar_copy_idempotente(cur, tabla, cols, filas, limites)
                    resumen.append((tabla, ins, omi, time.perf_counter() - t0))

                cur.execute("SELECT contenido_id FROM peliculas;")
                pelis_ids_ok = {r[0] for r in cur.fetchall()}
                idiomas_ok = [f for f in datos_csv["idiomas"] if f[0] in pelis_ids_ok]

                t0 = time.perf_counter()
                ins, omi = ejecutar_copy_idempotente(
                    cur, "pelicula_idiomas", ["contenido_id", "idioma"], idiomas_ok, limites
                )
                resumen.append(("pelicula_idiomas", ins, omi, time.perf_counter() - t0))

                cur.execute("SELECT libro_id FROM libros;")
                libros_ids_ok = {r[0] for r in cur.fetchall()}
                cur.execute("SELECT comic_id FROM comics;")
                comics_ids_ok = {r[0] for r in cur.fetchall()}

                basada_ok = [
                    f for f in sint["basada_en"]
                    if f[0] in prods_db
                    and (f[1] is None or f[1] in libros_ids_ok)
                    and (f[2] is None or f[2] in comics_ids_ok)
                ]
                t0 = time.perf_counter()
                ins, omi = ejecutar_copy_idempotente(
                    cur, "esta_basada_en", ["contenido_id", "libro_id", "comic_id"], basada_ok, limites
                )
                resumen.append(("esta_basada_en", ins, omi, time.perf_counter() - t0))

                t0 = time.perf_counter()
                ins, omi = ejecutar_copy_idempotente(
                    cur,
                    "usuarios",
                    ["usuario_id", "correo", "fecha_registro", "nombre", "apellidos", "tipo_usuario"],
                    sint["usuarios"],
                    limites,
                )
                resumen.append(("usuarios", ins, omi, time.perf_counter() - t0))

                cur.execute("SELECT usuario_id, tipo_usuario FROM usuarios;")
                usuarios_db = cur.fetchall()
                usuarios_set = set(usuarios_db)

                estandar_ok = [f for f in sint["estandar"] if (f[0], f[1]) in usuarios_set]
                premium_ok = [f for f in sint["premium"] if (f[0], f[1]) in usuarios_set]

                for tabla, cols, filas in [
                    ("usuario_estandar", ["usuario_id", "tipo_usuario", "limite_resenas", "publicidad"], estandar_ok),
                    ("usuario_premium", ["usuario_id", "tipo_usuario", "metodo_pago", "fecha_renovacion"], premium_ok),
                ]:
                    t0 = time.perf_counter()
                    ins, omi = ejecutar_copy_idempotente(cur, tabla, cols, filas, limites)
                    resumen.append((tabla, ins, omi, time.perf_counter() - t0))

                resenas_ok, visualiza_ok = generar_interacciones(usuarios_db, contenidos_ids_ok, offset_id=OFFSET)

                for tabla, cols, filas in [
                    ("resenas", ["resena_id", "puntuacion", "comentario", "fecha", "usuario_id", "contenido_id"], resenas_ok),
                    ("visualiza", ["usuario_id", "contenido_id", "porcentaje_avance", "fecha_reproduccion", "estado"], visualiza_ok),
                ]:
                    t0 = time.perf_counter()
                    ins, omi = ejecutar_copy_idempotente(cur, tabla, cols, filas, limites)
                    resumen.append((tabla, ins, omi, time.perf_counter() - t0))

                sincronizar_secuencias(cur)

        t_total = time.perf_counter() - t_inicio_total

        print("\n--- RESUMEN DE POBLACION POR TABLA ---")
        print(f"{'Tabla':<26} | {'Insertados':>10} | {'Omitidos':>10} | {'Tiempo (s)':>10}")
        print("-" * 66)
        total_ins = 0
        for tabla, ins, omi, dur in resumen:
            total_ins += ins
            print(f"{tabla:<26} | {ins:>10} | {omi:>10} | {dur:>10.4f}")
        print("-" * 66)
        print(f"{'TOTAL':<26} | {total_ins:>10} | {'-':>10} | {t_total:>10.4f}")

        print("\n--- COMPARATIVA DE RENDIMIENTO (COPY vs INSERT) ---")
        print(f"1,000 filas con INSERT individual : {t_insert_1000:.4f} s")
        print(f"{len(prods_ok)} filas con COPY masivo     : {t_copy_prods:.4f} s")
        print("\n[OK] Transaccion confirmada exitosamente (COMMIT).")

    except Exception as e:
        print(f"\n[ERROR CRITICO - ROLLBACK EJECUTADO]\nDetalle: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
    