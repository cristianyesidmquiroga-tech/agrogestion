@echo off
setlocal
cd /d "%~dp0"

if not exist ".env" (
    echo Preparando la configuracion local...
    copy /y ".env.example" ".env" >nul
    if errorlevel 1 goto error_env
)

if not exist ".venv\Scripts\python.exe" (
    echo Creando el entorno virtual...
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 -m venv .venv
    ) else (
        where python >nul 2>&1
        if errorlevel 1 goto error_python
        python -m venv .venv
    )
    if errorlevel 1 goto error_venv
)

".venv\Scripts\python.exe" -m scripts.local_config
if errorlevel 1 goto error_secret

".venv\Scripts\python.exe" -c "import fastapi, uvicorn, sqlalchemy, alembic, aiosqlite, asyncpg" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias. Esto puede tardar la primera vez...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto error_dependencies
)

echo Aplicando migraciones...
".venv\Scripts\python.exe" -m alembic upgrade head
if errorlevel 1 goto error_migrations

".venv\Scripts\python.exe" -m scripts.local_admin
if errorlevel 1 goto error_local_admin

echo Iniciando FastAPI. Documentacion: http://127.0.0.1:8000/docs
".venv\Scripts\python.exe" -m uvicorn app.main:app --reload
if errorlevel 1 goto error_server

endlocal
exit /b 0

:error_python
echo No se encontro Python. Instale Python 3.12 o superior y vuelva a abrir este archivo.
goto error

:error_venv
echo No se pudo crear el entorno virtual.
goto error

:error_env
echo No se pudo crear .env desde .env.example.
goto error

:error_secret
echo No se pudo generar JWT_SECRET. Revise que .env.example tenga esa variable.
goto error

:error_dependencies
echo No se pudieron instalar las dependencias. Revise su conexion a internet.
goto error

:error_migrations
echo Fallaron las migraciones. Revise la configuracion de .env y la base de datos.
goto error

:error_local_admin
echo No se pudo configurar el admin local. Este lanzador requiere desarrollo con SQLite.
goto error

:error_server
echo FastAPI termino con un error.
goto error

:error
pause
endlocal
exit /b 1
