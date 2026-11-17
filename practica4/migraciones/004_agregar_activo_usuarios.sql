-- Migración 004: agregar eliminación lógica a usuarios

ALTER TABLE usuarios
ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE;