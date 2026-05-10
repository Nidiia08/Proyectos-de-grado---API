-- =====================================================
-- Agrega datos personales a la tabla USUARIO
-- Cambio documentado para el sistema de seguimiento de trabajos de grado
-- =====================================================

ALTER TABLE USUARIO
  ADD COLUMN IF NOT EXISTS tipo_documento VARCHAR(30),
  ADD COLUMN IF NOT EXISTS numero_documento VARCHAR(20),
  ADD COLUMN IF NOT EXISTS celular VARCHAR(10);

UPDATE USUARIO
SET tipo_documento = COALESCE(tipo_documento, 'CEDULA_CIUDADANIA');

UPDATE USUARIO
SET numero_documento = COALESCE(numero_documento, LPAD(id::text, 10, '0'));

UPDATE USUARIO
SET celular = COALESCE(celular, LPAD((3000000000 + id)::text, 10, '0'));

ALTER TABLE USUARIO
  ALTER COLUMN tipo_documento SET DEFAULT 'CEDULA_CIUDADANIA',
  ALTER COLUMN tipo_documento SET NOT NULL,
  ALTER COLUMN numero_documento SET NOT NULL,
  ALTER COLUMN celular SET NOT NULL;

ALTER TABLE USUARIO
  ADD CONSTRAINT chk_usuario_tipo_documento
  CHECK (tipo_documento IN (
    'CEDULA_CIUDADANIA',
    'TARJETA_IDENTIDAD',
    'CEDULA_EXTRANJERIA',
    'PASAPORTE'
  ));

ALTER TABLE USUARIO
  ADD CONSTRAINT uq_usuario_numero_documento UNIQUE (numero_documento);

ALTER TABLE USUARIO
  ALTER COLUMN tipo_documento DROP DEFAULT;