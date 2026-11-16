# Documentación de Claves Foráneas y Modelo EER (`dwsismos`)

En esta sección se detalla el mapeo entre el modelo conceptual y la implementación física en PostgreSQL para garantizar la integridad referencial del *Data Warehouse*.

## Tabla de Claves Foráneas

| Clave Foránea (Columna) | Tabla Origen | Tabla Referenciada (Columna) | Relación del Modelo EER | ¿Admite Nulos? (Cardinalidad Mínima) | Justificación / Observaciones |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_sismo` | `fact_impacto_sismos_imputed` | `dim_sismos` (`id_sismo`) | Relación 1:N (Un sismo se relaciona con múltiples registros de impacto en la tabla de hechos). | **NO** (`NOT NULL`) | Cardinalidad mínima 1: Cada registro de impacto de sismo depende obligatoriamente de un evento sísmico registrado. |
| `id_zona` | `fact_impacto_sismos_imputed` | `dim_zonas` (`id_zona`) | Relación 1:N (Una zona geográfica agrupa múltiples registros de impacto sísmico). | **NO** (`NOT NULL`) | Cardinalidad mínima 1: Es indispensable ubicar geográficamente el evento en la zona correspondiente. |
| `id_tiempo` | `fact_impacto_sismos_imputed` | `dim_tiempo` (`id_tiempo`) | Relación 1:N (Un bloque temporal agrupa múltiples registros de sismos). | **NO** (`NOT NULL`) | Cardinalidad mínima 1: Todo evento analítico requiere una referencia temporal exacta. |
| `id_economia` | `fact_impacto_sismos_imputed` | `dim_economia` (`id_economia`) | Relación 1:N o 1:1 según afectación económica asociada al evento. | **SÍ / NO** *(según diseño)* | Si un sismo no cuenta con datos económicos reportados, se permite valor nulo (`NULL`) o se enlaza a un registro por defecto. |

---

## Justificación de Relaciones y Decisiones de Diseño

1. **Integridad en el Esquema en Estrella:** 
   Las dimensiones (`dim_sismos`, `dim_zonas`, `dim_tiempo`, `dim_economia`) actúan como entidades padre que proporcionan el contexto analítico, mientras que la tabla de hechos `fact_impacto_sismos_imputed` concentra las métricas cuantitativas del sistema.
2. **Relaciones omitidas o excepciones:**
   * En ciertos modelos analíticos de gran volumen de datos, las restricciones de claves foráneas directas suelen omitirse temporalmente para optimizar procesos masivos de carga (ETL), delegando la consistencia referencial a los scripts de limpieza previos. Sin embargo, para este proyecto se han implementado explícitamente para asegurar la consistencia estructural del dominio sísmico.
