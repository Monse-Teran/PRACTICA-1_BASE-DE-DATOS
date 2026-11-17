-- Migracion: Ampliar el limite de caracteres de la columna director
-- Justificacion: En netflix_titles.csv se detectaron 14 producciones codirigidas
-- cuyos nombres superan los 100 caracteres originales.

ALTER TABLE produccion_audiovisual
    ALTER COLUMN director TYPE VARCHAR(255);
    