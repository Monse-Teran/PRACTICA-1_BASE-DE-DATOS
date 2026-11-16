# Gestión de Usuarios y Permisos - Ejercicio 1.6
## 1. Definición de Roles (Principio de Mínimo Privilegio)

Para garantizar la seguridad de la base de datos `db_practica3`, se definen dos roles principales con alcances diferenciados:

- **`rol_invitado`:** Diseñado para usuarios no autenticados o con acceso general.
- **`rol_operador`:** Diseñado para usuarios con permisos de inserción, actualización y consulta sobre las tablas.
## 2. Creación de Roles y Usuarios en PostgreSQL

- **Sentencia SQL para los roles base:**
  ```sql
  CREATE ROLE rol_invitado NOLOGIN;
  CREATE ROLE rol_operador NOLOGIN;
  ```

- **Sentencia SQL para usuarios individuales y asignación:**
  ```sql
  CREATE USER ana_invitada WITH PASSWORD 'invitado_123';
  CREATE USER carlos_operador WITH PASSWORD 'operador_123';

  GRANT rol_invitado TO ANA;
  GRANT rol_operador TO CARLOS;
  ```
  **Evidencia**
  <img width="1410" height="424" alt="image" src="https://github.com/user-attachments/assets/b1805785-d5aa-4175-874d-9690ce88cc07" />

  ## 3. Asignación de Privilegios (GRANT)

- **Privilegios para el rol de consulta (`rol_invitado`):**
  Se otorga acceso exclusivo de lectura (`SELECT`) sobre las tablas del catálogo público.
  ```sql
  GRANT SELECT ON produccion_audiovisual, libros, comics, resenas TO rol_invitado;
  ```

- **Privilegios para el rol de gestión (`rol_operador`):**
  Se otorgan permisos completos de manipulación de datos (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) sobre las tablas transaccionales e interactivas.
  ```sql
  GRANT SELECT, INSERT, UPDATE, DELETE ON playlist, visualiza, resenas TO rol_operador;
  ```
  **Evidencia**
  <img width="1281" height="171" alt="image" src="https://github.com/user-attachments/assets/419da5a0-1b1f-4048-aab9-03f3e9bf3afe" />

  ## 4. Revocación de Privilegios (REVOKE)

  **Sentencia SQL para restringir accesos administrativos:**
  Se restringen explícitamente los accesos administrativos o de modificación al esquema público.
  ```sql
  REVOKE ALL PRIVILEGES ON DATABASE db_practica3 FROM rol_invitado;
  REVOKE CREATE ON SCHEMA public FROM rol_invitado, rol_operador;
  ```
  **Evidencia**
  <img width="1095" height="151" alt="image" src="https://github.com/user-attachments/assets/98ec5abd-f037-4519-aee4-c370345f18ee" />
## 5. Matriz de Permisos del Sistema

| Objeto / Tabla | `rol_invitado` | `rol_operador` | `postgres` (Admin) |
| :--- | :---: | :---: | :---: |
| `usuarios` | Solo lectura propia | Lectura y Escritura | Control Total |
| `libros` / `comics` | `SELECT` | `SELECT`, `INSERT`, `UPDATE` | Control Total |
| `produccion_audiovisual` | `SELECT` | `SELECT`, `INSERT`, `UPDATE` | Control Total |
| `playlist` / `visualiza` | Sin acceso | `SELECT`, `INSERT`, `UPDATE`, `DELETE` | Control Total |
| `resenas` | `SELECT` | `SELECT`, `INSERT`, `UPDATE`, `DELETE` | Control Total |

## Comprobacion de Permisos
<img width="940" height="490" alt="image" src="https://github.com/user-attachments/assets/ea2cc5fe-0aec-43a7-a935-9c555486b78e" />

## Conexión con usuario ANA y comprobación de lectura
<img width="962" height="214" alt="image" src="https://github.com/user-attachments/assets/101af1d0-7970-4635-8c6d-4124c77a531d" />




