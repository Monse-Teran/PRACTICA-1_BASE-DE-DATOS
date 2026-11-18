-- Creación de tabla de Infraestructura Crítica
CREATE TABLE INFRAESTRUCTURA_CRITICA (
    id_inmueble SERIAL PRIMARY KEY,
    nombre_inmueble VARCHAR(150) NOT NULL,
    tipo_inmueble VARCHAR(50) NOT NULL,
    id_zona INT NOT NULL,
    estatus_operativo VARCHAR(100) NOT NULL
);

-- Creación de tabla de Reportes de Incidencias
CREATE TABLE REPORTE_INCIDENCIA_INMUEBLE (
    id_reporte SERIAL PRIMARY KEY,
    id_inmueble INT NOT NULL,
    nivel_dano VARCHAR(50) NOT NULL,
    necesidad VARCHAR(255) NOT NULL,
    fecha_hora_reporte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_inmueble_reporte FOREIGN KEY (id_inmueble) 
        REFERENCES INFRAESTRUCTURA_CRITICA(id_inmueble)
);

-- Creación de tabla para el Requisito Extra de IA
CREATE TABLE PREDICCION_URGENCIA_IA (
    id_prediccion SERIAL PRIMARY KEY,
    id_reporte INT NOT NULL,
    nivel_prioridad_calculado INT NOT NULL,
    confianza_modelo FLOAT NOT NULL,
    version_modelo VARCHAR(50) NOT NULL,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reporte_ia FOREIGN KEY (id_reporte) 
        REFERENCES REPORTE_INCIDENCIA_INMUEBLE(id_reporte)
);
