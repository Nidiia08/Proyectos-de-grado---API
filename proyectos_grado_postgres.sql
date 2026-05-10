-- =====================================================
-- SISTEMA DE SEGUIMIENTO DE TRABAJOS DE GRADO
-- Universidad de Nariño - Departamento de Sistemas
-- PostgreSQL 16
-- =====================================================

-- =========================
-- TABLA USUARIO
-- =========================
CREATE TABLE USUARIO (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  correo VARCHAR(150) NOT NULL UNIQUE,
    tipo_documento VARCHAR(30) NOT NULL DEFAULT 'CEDULA_CIUDADANIA'
        CHECK (tipo_documento IN (
            'CEDULA_CIUDADANIA',
            'TARJETA_IDENTIDAD',
            'CEDULA_EXTRANJERIA',
            'PASAPORTE'
        )),
    numero_documento VARCHAR(20) NOT NULL UNIQUE,
    celular VARCHAR(10) NOT NULL,
  "password" VARCHAR(255) NOT NULL,
  activo BOOLEAN DEFAULT TRUE,
  fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP DEFAULT NULL,
  is_superuser BOOLEAN DEFAULT FALSE
);

-- =========================
-- TABLA ROL
-- =========================
CREATE TABLE USUARIO_ROL (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    rol VARCHAR(20) NOT NULL
        CHECK (rol IN ('ESTUDIANTE', 'DOCENTE', 'JURADO', 'COMITE')),
    CONSTRAINT fk_ur_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES USUARIO(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_usuario_rol
        UNIQUE (usuario_id, rol)
);

-- =========================
-- TABLA ESTUDIANTE
-- =========================
CREATE TABLE ESTUDIANTE (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL UNIQUE,
    codigo_estudiante VARCHAR(50) NOT NULL UNIQUE,
    programa VARCHAR(150) NOT NULL,
    promedio_acumulado DECIMAL(3,2),
    creditos_aprobados INT,
    CONSTRAINT fk_estudiante_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES USUARIO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLA DOCENTE
-- =========================
CREATE TABLE DOCENTE (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL UNIQUE,
    codigo_docente VARCHAR(50) NOT NULL UNIQUE,
    area_conocimiento VARCHAR(150),
    max_proyectos_asesor INT DEFAULT 5,
    max_proyectos_jurado INT DEFAULT 5,
    CONSTRAINT fk_docente_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES USUARIO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLA PERIODO_ACADEMICO
-- =========================
CREATE TABLE PERIODO_ACADEMICO (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    activo BOOLEAN DEFAULT FALSE
);

-- =========================
-- TABLA PROYECTO
-- =========================
CREATE TABLE PROYECTO (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(300) NOT NULL,
    modalidad VARCHAR(30) NOT NULL CHECK (modalidad IN ('INVESTIGACION', 'INTERACCION_SOCIAL')),
    subtipo VARCHAR(50) CHECK (subtipo IN ('PASANTIA', 'DESARROLLO_SOFTWARE', 'INTERVENCION')),
    estado VARCHAR(30) NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'FINALIZADO', 'CANCELADO', 'REPROBADO')),
    fase_actual VARCHAR(30) NOT NULL DEFAULT 'INSCRIPCION' CHECK (fase_actual IN ('INSCRIPCION', 'APROBACION', 'DESARROLLO', 'CULMINACION', 'EVALUACION')),
    fecha_inicio DATE,
    fecha_fin_estimada DATE,
    fecha_fin_real DATE,
    periodo_academico_id INT NOT NULL,
    asesor_id INT NOT NULL,
    coasesor_id INT,
    es_interdisciplinario BOOLEAN DEFAULT FALSE,
    es_grupo BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_proyecto_periodo
        FOREIGN KEY (periodo_academico_id)
        REFERENCES PERIODO_ACADEMICO(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_proyecto_asesor
        FOREIGN KEY (asesor_id)
        REFERENCES DOCENTE(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_proyecto_coasesor
        FOREIGN KEY (coasesor_id)
        REFERENCES DOCENTE(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =========================
-- TABLA PROYECTO_ESTUDIANTE
-- =========================
CREATE TABLE PROYECTO_ESTUDIANTE (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL,
    estudiante_id INT NOT NULL,
    es_autor_principal BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_pe_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_pe_estudiante
        FOREIGN KEY (estudiante_id)
        REFERENCES ESTUDIANTE(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_proyecto_estudiante UNIQUE (proyecto_id, estudiante_id)
);

-- =========================
-- TABLA ACUERDO
-- =========================
CREATE TABLE ACUERDO (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL,
    numero_acuerdo VARCHAR(50) NOT NULL UNIQUE,
    tipo VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    descripcion TEXT,
    generado_por INT NOT NULL,
    CONSTRAINT fk_acuerdo_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_acuerdo_usuario
        FOREIGN KEY (generado_por)
        REFERENCES USUARIO(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =========================
-- TABLA FASE_INSCRIPCION
-- =========================
CREATE TABLE FASE_INSCRIPCION (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL UNIQUE,
    fecha_limite DATE,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'ENVIADO', 'EN_REVISION', 'APROBADO', 'CON_OBSERVACIONES')),
    comentario_estudiante TEXT,
    observaciones_comite TEXT,
    fecha_envio TIMESTAMP,
    fecha_aprobacion TIMESTAMP,
    CONSTRAINT fk_fi_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLA DOCUMENTO_INSCRIPCION
-- =========================
CREATE TABLE DOCUMENTO_INSCRIPCION (
    id SERIAL PRIMARY KEY,
    fase_inscripcion_id INT NOT NULL,
    estudiante_id INT NOT NULL,
    nombre_documento VARCHAR(200) NOT NULL,
    tipo_documento VARCHAR(100) NOT NULL,
    archivo_url VARCHAR(500),
    estado VARCHAR(30) NOT NULL DEFAULT 'SIN_CARGAR' CHECK (estado IN ('SIN_CARGAR', 'CARGADO', 'APROBADO', 'RECHAZADO')),
    es_requerido BOOLEAN DEFAULT TRUE,
    fecha_carga TIMESTAMP,
    observacion_rechazo TEXT,
    CONSTRAINT fk_di_fase
        FOREIGN KEY (fase_inscripcion_id)
        REFERENCES FASE_INSCRIPCION(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_di_estudiante
        FOREIGN KEY (estudiante_id)
        REFERENCES ESTUDIANTE(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLA FASE_APROBACION
-- =========================
CREATE TABLE FASE_APROBACION (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL UNIQUE,
    iteracion_actual INT DEFAULT 1,
    max_iteraciones INT NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'EN_REVISION', 'CON_OBSERVACIONES', 'APROBADO')),
    CONSTRAINT fk_fa_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLA ITERACION_APROBACION
-- =========================
CREATE TABLE ITERACION_APROBACION (
    id SERIAL PRIMARY KEY,
    fase_aprobacion_id INT NOT NULL,
    numero_iteracion INT NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'EN_REVISION', 'CON_OBSERVACIONES', 'APROBADA')),
    fecha_inicio DATE,
    dias_habiles_jurado INT DEFAULT 5,
    dias_habiles_estudiante INT,
    fecha_limite_jurado DATE,
    fecha_limite_estudiante DATE,
    archivo_propuesta_url VARCHAR(500),
    comentario_estudiante TEXT,
    fecha_envio_estudiante TIMESTAMP,
    CONSTRAINT fk_ia_fase
        FOREIGN KEY (fase_aprobacion_id)
        REFERENCES FASE_APROBACION(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_iteracion UNIQUE (fase_aprobacion_id, numero_iteracion)
);

-- =========================
-- TABLA REVISION_JURADO_REVISOR
-- =========================
CREATE TABLE REVISION_JURADO_REVISOR (
    id SERIAL PRIMARY KEY,
    iteracion_aprobacion_id INT NOT NULL,
    jurado_id INT NOT NULL,
    decision VARCHAR(30) NOT NULL CHECK (decision IN ('CON_OBSERVACIONES', 'APROBADA')),
    observaciones TEXT,
    fecha_respuesta TIMESTAMP,
    CONSTRAINT fk_rjr_iteracion
        FOREIGN KEY (iteracion_aprobacion_id)
        REFERENCES ITERACION_APROBACION(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_rjr_jurado
        FOREIGN KEY (jurado_id)
        REFERENCES DOCENTE(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =========================
-- TABLA FASE_DESARROLLO
-- =========================
CREATE TABLE FASE_DESARROLLO (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL UNIQUE,
    fecha_inicio DATE,
    fecha_fin_estimada DATE,
    estado VARCHAR(30) NOT NULL DEFAULT 'EN_CURSO' CHECK (estado IN ('EN_CURSO', 'FINALIZADO', 'PRORROGADO')),
    tiene_prorroga BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_fd_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLA PRORROGA
-- =========================
CREATE TABLE PRORROGA (
    id SERIAL PRIMARY KEY,
    fase_desarrollo_id INT NOT NULL,
    fecha_anterior DATE NOT NULL,
    fecha_nueva DATE NOT NULL,
    motivo TEXT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    registrado_por INT NOT NULL,
    CONSTRAINT fk_prorroga_fase
        FOREIGN KEY (fase_desarrollo_id)
        REFERENCES FASE_DESARROLLO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_prorroga_usuario
        FOREIGN KEY (registrado_por)
        REFERENCES USUARIO(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =========================
-- TABLA INFORME_TRIMESTRAL
-- =========================
CREATE TABLE INFORME_TRIMESTRAL (
    id SERIAL PRIMARY KEY,
    fase_desarrollo_id INT NOT NULL,
    numero_informe INT NOT NULL,
    fecha_limite DATE,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'ENVIADO', 'APROBADO', 'CON_OBSERVACIONES')),
    archivo_url VARCHAR(500),
    comentario_estudiante TEXT,
    observaciones_comite TEXT,
    observaciones_asesor TEXT,
    fecha_envio TIMESTAMP,
    fecha_aprobacion TIMESTAMP,
    CONSTRAINT fk_it_fase
        FOREIGN KEY (fase_desarrollo_id)
        REFERENCES FASE_DESARROLLO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_informe UNIQUE (fase_desarrollo_id, numero_informe)
);

-- =========================
-- TABLA FASE_CULMINACION
-- =========================
CREATE TABLE FASE_CULMINACION (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL UNIQUE,
    fecha_limite DATE,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'ENVIADO', 'EN_REVISION', 'APROBADO', 'CON_OBSERVACIONES')),
    enlace_nube VARCHAR(500),
    comentario_estudiante TEXT,
    fecha_envio TIMESTAMP,
    fecha_aprobacion TIMESTAMP,
    CONSTRAINT fk_fc_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLA DOCUMENTO_CULMINACION
-- =========================
CREATE TABLE DOCUMENTO_CULMINACION (
    id SERIAL PRIMARY KEY,
    fase_culminacion_id INT NOT NULL,
    estudiante_id INT NOT NULL,
    nombre_documento VARCHAR(200) NOT NULL,
    tipo_documento VARCHAR(100) NOT NULL,
    archivo_url VARCHAR(500),
    estado VARCHAR(30) NOT NULL DEFAULT 'SIN_CARGAR' CHECK (estado IN ('SIN_CARGAR', 'CARGADO', 'APROBADO', 'RECHAZADO')),
    es_requerido BOOLEAN DEFAULT TRUE,
    fecha_carga TIMESTAMP,
    observacion_rechazo TEXT,
    CONSTRAINT fk_dc_fase
        FOREIGN KEY (fase_culminacion_id)
        REFERENCES FASE_CULMINACION(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_dc_estudiante
        FOREIGN KEY (estudiante_id)
        REFERENCES ESTUDIANTE(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLA FASE_EVALUACION
-- =========================
CREATE TABLE FASE_EVALUACION (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL UNIQUE,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'EN_REVISION', 'SUSTENTACION_PROGRAMADA', 'FINALIZADO')),
    fecha_sustentacion_privada TIMESTAMP,
    fecha_socializacion_publica TIMESTAMP,
    socializacion_confirmada BOOLEAN DEFAULT FALSE,
    asistentes_socializacion INT DEFAULT 0,
    nota_final DECIMAL(5,2),
    resultado VARCHAR(20) CHECK (resultado IN ('APROBADO', 'REPROBADO', 'MERITORIO', 'LAUREADO')),
    fecha_acta TIMESTAMP,
    CONSTRAINT fk_fe_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLA ASIGNACION_JURADO
-- =========================
CREATE TABLE ASIGNACION_JURADO (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL,
    jurado_id INT NOT NULL,
    tipo_jurado VARCHAR(20) NOT NULL CHECK (tipo_jurado IN ('REVISOR', 'EVALUADOR')),
    fecha_asignacion DATE DEFAULT CURRENT_DATE,
    activo BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_aj_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_aj_jurado
        FOREIGN KEY (jurado_id)
        REFERENCES DOCENTE(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uq_asignacion UNIQUE (proyecto_id, jurado_id, tipo_jurado)
);

-- =========================
-- TABLA CALIFICACION_JURADO
-- =========================
CREATE TABLE CALIFICACION_JURADO (
    id SERIAL PRIMARY KEY,
    fase_evaluacion_id INT NOT NULL,
    jurado_id INT NOT NULL,
    cumplimiento_objetivos INT NOT NULL CHECK (cumplimiento_objetivos BETWEEN 0 AND 25),
    originalidad_creatividad INT NOT NULL CHECK (originalidad_creatividad BETWEEN 0 AND 10),
    validez_conclusiones INT NOT NULL CHECK (validez_conclusiones BETWEEN 0 AND 15),
    organizacion_presentacion INT NOT NULL CHECK (organizacion_presentacion BETWEEN 0 AND 10),
    sustentacion_privada INT NOT NULL CHECK (sustentacion_privada BETWEEN 0 AND 30),
    socializacion_publica INT NOT NULL CHECK (socializacion_publica BETWEEN 0 AND 10),
    total_documento INT GENERATED ALWAYS AS (
        cumplimiento_objetivos + originalidad_creatividad +
        validez_conclusiones + organizacion_presentacion
    ) STORED,
    total_sustentacion INT GENERATED ALWAYS AS (
        sustentacion_privada + socializacion_publica
    ) STORED,
    total_final INT GENERATED ALWAYS AS (
        cumplimiento_objetivos + originalidad_creatividad +
        validez_conclusiones + organizacion_presentacion +
        sustentacion_privada + socializacion_publica
    ) STORED,
    observaciones_finales TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    enviada BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_cj_fase
        FOREIGN KEY (fase_evaluacion_id)
        REFERENCES FASE_EVALUACION(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_cj_jurado
        FOREIGN KEY (jurado_id)
        REFERENCES DOCENTE(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uq_calificacion UNIQUE (fase_evaluacion_id, jurado_id)
);

-- =========================
-- TABLA REVISTA_INDEXADA
-- =========================
CREATE TABLE REVISTA_INDEXADA (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL UNIQUE,
    nombre_revista VARCHAR(300) NOT NULL,
    clasificacion VARCHAR(5) NOT NULL CHECK (clasificacion IN ('A1', 'A', 'B', 'C')),
    calificacion_equivalente INT GENERATED ALWAYS AS (
        CASE clasificacion
            WHEN 'A1' THEN 100
            WHEN 'A'  THEN 100
            WHEN 'B'  THEN 90
            WHEN 'C'  THEN 80
        END
    ) STORED,
    isbn_issn VARCHAR(50),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ri_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLA PLANTILLA
-- =========================
CREATE TABLE PLANTILLA (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    fase VARCHAR(30) NOT NULL CHECK (fase IN ('INSCRIPCION', 'APROBACION', 'DESARROLLO', 'CULMINACION', 'EVALUACION')),
    modalidad_aplica VARCHAR(30) DEFAULT 'TODAS' CHECK (modalidad_aplica IN ('TODAS', 'INVESTIGACION', 'INTERACCION_SOCIAL', 'PASANTIA')),
    archivo_url VARCHAR(500) NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subida_por INT NOT NULL,
    CONSTRAINT fk_plantilla_usuario
        FOREIGN KEY (subida_por)
        REFERENCES USUARIO(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =========================
-- TABLA NOTIFICACION
-- =========================
CREATE TABLE NOTIFICACION (
    id SERIAL PRIMARY KEY,
    usuario_destino_id INT NOT NULL,
    proyecto_id INT,
    tipo VARCHAR(100) NOT NULL,
    mensaje TEXT NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    url_accion VARCHAR(500),
    CONSTRAINT fk_notif_usuario
        FOREIGN KEY (usuario_destino_id)
        REFERENCES USUARIO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_notif_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLA HISTORIAL_ACCION
-- =========================
CREATE TABLE HISTORIAL_ACCION (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL,
    usuario_id INT NOT NULL,
    accion VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fase VARCHAR(30) CHECK (fase IN ('INSCRIPCION', 'APROBACION', 'DESARROLLO', 'CULMINACION', 'EVALUACION')),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ha_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_ha_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES USUARIO(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =========================
-- TABLA CONFIGURACION_SISTEMA
-- =========================
CREATE TABLE CONFIGURACION_SISTEMA (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) NOT NULL UNIQUE,
    valor VARCHAR(255) NOT NULL,
    descripcion TEXT,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_por INT NOT NULL,
    CONSTRAINT fk_cs_usuario
        FOREIGN KEY (actualizado_por)
        REFERENCES USUARIO(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =========================
-- TABLA CONVERSACION
-- =========================
CREATE TABLE CONVERSACION (
    id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL,
    estudiante_id INT NOT NULL,
    docente_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_conv_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES PROYECTO(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_conv_estudiante
        FOREIGN KEY (estudiante_id)
        REFERENCES ESTUDIANTE(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_conv_docente
        FOREIGN KEY (docente_id)
        REFERENCES DOCENTE(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_conversacion UNIQUE (proyecto_id, estudiante_id, docente_id)
);

-- =========================
-- TABLA MENSAJE
-- =========================
CREATE TABLE MENSAJE (
    id SERIAL PRIMARY KEY,
    conversacion_id INT NOT NULL,
    remitente_id INT NOT NULL,
    contenido TEXT NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    leido BOOLEAN DEFAULT FALSE,
    fecha_lectura TIMESTAMP,
    CONSTRAINT fk_msg_conversacion
        FOREIGN KEY (conversacion_id)
        REFERENCES CONVERSACION(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_msg_remitente
        FOREIGN KEY (remitente_id)
        REFERENCES USUARIO(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =====================================================
-- DATOS INICIALES — CONFIGURACION_SISTEMA
-- =====================================================
-- Requiere que exista al menos un usuario con rol COMITE
-- Insertar después de crear el primer usuario del comité

-- INSERT INTO CONFIGURACION_SISTEMA (clave, valor, descripcion, actualizado_por) VALUES
-- ('dias_revision_jurado', '5', 'Días hábiles para que el jurado revisor analice la propuesta', 1),
-- ('dias_ajuste_inv_iter1', '10', 'Días hábiles para ajustes del estudiante en iteración 1 (Investigación)', 1),
-- ('dias_ajuste_inv_iter2', '5', 'Días hábiles para ajustes del estudiante en iteración 2 y 3 (Investigación)', 1),
-- ('dias_ajuste_soc_iter1', '15', 'Días hábiles para ajustes del estudiante en iteración 1 (Interacción Social)', 1),
-- ('dias_ajuste_soc_iter2', '5', 'Días hábiles para ajustes del estudiante en iteración 2 (Interacción Social)', 1),
-- ('dias_revision_informe_final', '20', 'Días para revisión del informe final por jurados evaluadores', 1),
-- ('dias_ajuste_eval_ronda1', '10', 'Días para ajustes del estudiante tras evaluación primera ronda', 1),
-- ('dias_ajuste_eval_ronda2', '5', 'Días para ajustes del estudiante tras evaluación segunda ronda', 1),
-- ('duracion_base_investigacion', '6', 'Duración base en meses para proyectos de Investigación', 1),
-- ('duracion_base_interaccion', '6', 'Duración base en meses para proyectos de Interacción Social', 1),
-- ('duracion_maxima_prorroga', '24', 'Duración máxima en meses con prórroga incluida', 1),
-- ('min_asistentes_socializacion', '10', 'Mínimo de estudiantes requeridos en socialización pública', 1),
-- ('max_proyectos_asesor', '5', 'Máximo de proyectos simultáneos por asesor', 1),
-- ('max_proyectos_jurado', '5', 'Máximo de proyectos simultáneos por jurado', 1),
-- ('correo_departamento', 'insistemas@udenar.edu.co', 'Correo institucional del Departamento de Sistemas', 1),
-- ('nombre_departamento', 'Departamento de Sistemas', 'Nombre oficial del departamento', 1);