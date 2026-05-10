-- =====================================================
-- Agrega coasesor a la tabla PROYECTO
-- =====================================================

ALTER TABLE PROYECTO
  ADD COLUMN IF NOT EXISTS coasesor_id INT;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'fk_proyecto_coasesor'
  ) THEN
    ALTER TABLE PROYECTO
      ADD CONSTRAINT fk_proyecto_coasesor
      FOREIGN KEY (coasesor_id)
      REFERENCES DOCENTE(id)
      ON DELETE RESTRICT
      ON UPDATE CASCADE;
  END IF;
END $$;