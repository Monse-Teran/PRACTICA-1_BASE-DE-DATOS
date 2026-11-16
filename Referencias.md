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
  
# 2.2 Acciones Referenciales
| Clave Foránea (`fact_impacto_sismos_imputed`) | Tabla Padre | Acción `ON DELETE` | Acción `ON UPDATE` | Justificación con Regla del Dominio |
| :--- | :--- | :--- | :--- | :--- |
| **`id_sismo`** | `dim_sismos` | `RESTRICT` | `CASCADE` | **Borrado:** Un evento sísmico registrado oficialmente no debe eliminarse mientras existan métricas de impacto asociadas en el historial analítico.<br>**Actualización:** Si se recodifica o corrige el identificador del sismo en el catálogo maestro, los hechos deben actualizarse automáticamente para no perder el vínculo. |
| **`id_zona`** | `dim_zonas` | `RESTRICT` | `CASCADE` | **Borrado:** No se puede eliminar una región geográfica o estado si ya cuenta con registros históricos de sismos ocurridos ahí.<br>**Actualización:** Si cambia la clave de regionalización (ej. actualización de códigos postales o claves INEGI), la referencia en la tabla de hechos debe seguir el cambio. |
| **`id_tiempo`** | `dim_tiempo` | `RESTRICT` | `CASCADE` | **Borrado:** Los registros del calendario dimensional son inmutables mientras existan eventos ocurridos en esa fecha.<br>**Actualización:** Si se reestructura el formato de la llave subrogada temporal, los hechos heredan la nueva clave. |
| **`id_economia`** | `dim_economia` | `SET NULL` | `CASCADE` | **Borrado:** Si se invalida o depura una estimación financiera preliminar (ej. por revisión de aseguradoras o gobierno), el registro del sismo y su impacto físico **deben sobrevivir** en el Data Warehouse sin quedar huérfanos.<br>**Actualización:** Si se actualiza la clave del reporte económico, la tabla de hechos actualiza su referencia. |

### Implementación SQL en PostgreSQL

```sql
-- 1. Relación con dim_sismos
ALTER TABLE fact_impacto_sismos_imputed
DROP CONSTRAINT IF EXISTS fk_fact_sismo,
ADD CONSTRAINT fk_fact_sismo
    FOREIGN KEY (id_sismo) REFERENCES dim_sismos(id_sismo)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;
```
# Evidencia
<img width="1356" height="272" alt="image" src="https://github.com/user-attachments/assets/33e53114-0443-425f-a32e-9bb1321f1320" />

-- 2. Relación con dim_zonas
```sql
ALTER TABLE fact_impacto_sismos_imputed
DROP CONSTRAINT IF EXISTS fk_fact_zona,
ADD CONSTRAINT fk_fact_zona
    FOREIGN KEY (id_zona) REFERENCES dim_zonas(id_zona)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;
```
# Evidencia
<img width="1434" height="213" alt="image" src="https://github.com/user-attachments/assets/92b6b187-2f59-4e59-b084-cf9017efb757" />

-- 3. Relación con dim_tiempo
```sql
ALTER TABLE fact_impacto_sismos_imputed
DROP CONSTRAINT IF EXISTS fk_fact_tiempo,
ADD CONSTRAINT fk_fact_tiempo
    FOREIGN KEY (id_tiempo) REFERENCES dim_tiempo(id_tiempo)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;
```
# Evidencia

<img width="1405" height="178" alt="image" src="https://github.com/user-attachments/assets/25927121-c5b9-4935-bf4e-3eeefca89a74" />

-- 4. Relación con dim_economia (admite nulos)
```sql
ALTER TABLE fact_impacto_sismos_imputed
DROP CONSTRAINT IF EXISTS fk_fact_economia,
ADD CONSTRAINT fk_fact_economia
    FOREIGN KEY (id_economia) REFERENCES dim_economia(id_economia)
    ON DELETE SET NULL
    ON UPDATE CASCADE;
```
# Evidencia
<img width="1388" height="180" alt="image" src="https://github.com/user-attachments/assets/f1b78752-33e7-4e47-832c-598f41c37669" />


