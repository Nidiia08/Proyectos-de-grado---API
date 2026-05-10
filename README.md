# Proyectos de Grado API

Backend del sistema de seguimiento de trabajos de grado con Django + PostgreSQL + Docker.

## Requisitos

- Docker Desktop
- Docker Compose

## 1) Configurar variables de entorno

Verifica que exista el archivo `.env` en la raíz del proyecto con los datos de base de datos.

## 2) Levantar contenedores

```bash
docker compose up -d --build
```

## 3) Ejecutar migraciones

```bash
docker compose exec api python manage.py migrate
```

## 4) Flujo correcto de autenticación en Postman

URL base local:

```text
http://localhost:8000/api
```

### 4.1 Preparar la base

Si vas a probar desde cero, ejecuta una sola vez por base de datos:

```bash
docker compose exec api python manage.py migrate token_blacklist
docker compose exec api python manage.py crear_comite
```

Datos por defecto del usuario inicial:

- Correo: `admin@udenar.edu.co`
- Contraseña: `Admin2024*`
- Rol: `COMITE`

Datos de administrador Django (opcional):
- Correo: `proyectos@udenar.edu.co`
- Password: `Proyectos123`

### 4.2 Crear variables en Postman

En tu entorno de Postman crea estas variables:

- `base_url` = `http://localhost:8000/api`
- `access_token` = vacío al inicio
- `refresh_token` = vacío al inicio

### 4.3 Hacer login

Petición `POST` a:

```text
{{base_url}}/auth/login/
```

Body -> `raw` -> `JSON`:

```json
{
	"correo": "admin@udenar.edu.co",
	"password": "Admin2024*",
	"rol": "COMITE"
}
```

Respuesta esperada:

- `access`
- `refresh`
- `rol_sesion`
- `debe_cambiar_password`
- `usuario`

Luego copia manualmente los valores de `access` y `refresh` en las variables `access_token` y `refresh_token`.

### 4.4 Probar un endpoint protegido

Petición `GET` a:

```text
{{base_url}}/auth/perfil/
```

Header:

```text
Authorization: Bearer {{access_token}}
```

Resultado esperado: devuelve los datos del usuario autenticado.

### 4.5 Cambiar la contraseña si aplica

Si la respuesta de login indica que debe cambiar contraseña, prueba:

```text
PATCH {{base_url}}/auth/cambiar-password/
```

Header:

```text
Authorization: Bearer {{access_token}}
```

Body -> `raw` -> `JSON`:

```json
{
	"password_actual": "Admin2024*",
	"password_nuevo": "NuevaClave2026*",
	"confirmar_password": "NuevaClave2026*"
}
```

Después vuelve a hacer login con la nueva contraseña y actualiza `access_token` y `refresh_token`.

### 4.6 Renovar el access token

Petición `POST` a:

```text
{{base_url}}/auth/refresh/
```

Body -> `raw` -> `JSON`:

```json
{
	"refresh": "{{refresh_token}}"
}
```

También acepta `refresh_token` si prefieres ese nombre.

Cuando responda con `access`, reemplaza el valor de `access_token`.

### 4.7 Cerrar sesión

Petición `POST` a:

```text
{{base_url}}/auth/logout/
```

Header:

```text
Authorization: Bearer {{access_token}}
```

Body -> `raw` -> `JSON`:

```json
{
	"refresh": "{{refresh_token}}"
}
```

Al cerrar sesión, el `refresh_token` queda inutilizable.

### 4.8 Crear un usuario estudiante

> **Requisito:** necesitas un usuario con rol `COMITE` autenticado (el `access_token`).

Petición `POST` a:

```text
{{base_url}}/usuarios/estudiantes/
```

Header:

```text
Authorization: Bearer {{access_token}}
```

Body -> `raw` -> `JSON`:

```json
{
	"nombre": "Juan",
	"apellido": "Pérez",
	"correo": "juan.perez@udenar.edu.co",
	"password": "EstudiantePass123*",
	"tipo_documento": "CEDULA_CIUDADANIA",
	"numero_documento": "1234567890",
	"celular": "3001234567",
	"codigo_estudiante": "2024001",
	"programa": "Ingeniería de Sistemas",
	"promedio_acumulado": 4.5,
	"creditos_aprobados": 120
}
```

**Campos requeridos:**
- `nombre`: máx 100 caracteres
- `apellido`: máx 100 caracteres
- `correo`: email válido y único
- `password`: contraseña (será encriptada)
- `tipo_documento`: `CEDULA_CIUDADANIA`, `TARJETA_IDENTIDAD`, `CEDULA_EXTRANJERIA`, o `PASAPORTE`
- `numero_documento`: máx 20 caracteres, debe ser único
- `celular`: exactamente 10 dígitos numéricos
- `codigo_estudiante`: máx 50 caracteres, debe ser único
- `programa`: máx 150 caracteres

**Campos opcionales:**
- `promedio_acumulado`: decimal con 2 decimales
- `creditos_aprobados`: número entero

Resultado esperado: código `201` y datos del estudiante creado.

## 5) Pruebas recomendadas en Postman

### Prueba 1: login correcto

- Método: `POST`
- URL: `http://localhost:8000/api/auth/login/`
- Body:

```json
{
	"correo": "admin@udenar.edu.co",
	"password": "Admin2024*",
	"rol": "COMITE"
}
```

Resultado esperado: código `200` y tokens JWT.

### Prueba 2: login con rol incorrecto

- Método: `POST`
- URL: `http://localhost:8000/api/auth/login/`
- Body:

```json
{
	"correo": "admin@udenar.edu.co",
	"password": "Admin2024*",
	"rol": "ESTUDIANTE"
}
```

Resultado esperado: error indicando que no tienes acceso con ese rol.

### Prueba 3: acceso a perfil sin token

- Método: `GET`
- URL: `{{base_url}}/auth/perfil/`

Resultado esperado: error `401` porque falta `Authorization`.

### Prueba 4: refresh del token

- Método: `POST`
- URL: `http://localhost:8000/api/auth/refresh/`
- Body:

```json
{
	"refresh": "<refresh>"
}
```

Resultado esperado: código `200` y nuevo `access`.

### Prueba 5: consultar perfil con token

- Método: `GET`
- URL: `http://localhost:8000/api/auth/perfil/`
- Header:

```text
Authorization: Bearer <access>
```

Resultado esperado: datos del usuario autenticado y su perfil, si aplica.

### Prueba 6: cambiar contraseña

- Método: `PATCH`
- URL: `{{base_url}}/auth/cambiar-password/`
- Header:

```text
Authorization: Bearer {{access_token}}
```
- Body:

```json
{
	"password_actual": "Admin2024*",
	"password_nuevo": "NuevaClave2026*",
	"confirmar_password": "NuevaClave2026*"
}
```

Resultado esperado: confirmación de actualización de contraseña.

### Prueba 7: cerrar sesión

- Método: `POST`
- URL: `http://localhost:8000/api/auth/logout/`
- Header:

```text
Authorization: Bearer <access>
```
- Body:

```json
{
	"refresh": "<refresh>"
}
```

Resultado esperado: sesión cerrada correctamente.

### Prueba 8: crear usuario estudiante

- Método: `POST`
- URL: `{{base_url}}/usuarios/estudiantes/`
- Header:

```text
Authorization: Bearer {{access_token}}
```
- Body:

```json
{
	"nombre": "Juan",
	"apellido": "Pérez",
	"correo": "juan.perez@udenar.edu.co",
	"password": "EstudiantePass123*",
	"tipo_documento": "CEDULA_CIUDADANIA",
	"numero_documento": "1234567890",
	"celular": "3001234567",
	"codigo_estudiante": "2024001",
	"programa": "Ingeniería de Sistemas",
	"promedio_acumulado": 4.5,
	"creditos_aprobados": 120
}
```

Resultado esperado: código `201` y datos del estudiante creado con su usuario.

## 6) Comandos importantes (ejecutar una vez por base de datos)

Crear usuario inicial del comité curricular:

```bash
docker compose exec api python manage.py crear_comite
```

Crear tablas de blacklist para JWT (logout/refresh):

```bash
docker compose exec api python manage.py migrate token_blacklist
```

## 7) Ver logs (opcional)

```bash
docker compose logs -f api
docker compose logs -f db
```

## 8) Detener contenedores

```bash
docker compose down
```

## 9) Eliminar contenedores, redes y volúmenes

```bash
docker compose down -v
```

## 10) Vaciar base de datos (opcional)

```bash
docker compose exec db psql -U proyectos_user -d proyectos_grado -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

## Nota

Si borras volúmenes (`docker compose down -v`) o cambias a una base de datos nueva/vacía, debes volver a ejecutar migraciones y el comando `crear_comite`.
