@echo off
REM Script de Instalación y Ejecución para Cyber-Inventory en Windows
REM Este script automatiza la instalación y puesta en marcha del MVP

setlocal enabledelayedexpansion

echo.
echo ========================================
echo    CYBER-INVENTORY - Setup Script
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Descarga Python desde: https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python detectado
python --version
echo.

REM Crear entorno virtual
echo Creando entorno virtual...
if not exist venv (
    python -m venv venv
    echo [OK] Entorno virtual creado
) else (
    echo [OK] Entorno virtual ya existe
)
echo.

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo [OK] Entorno virtual activado
echo.

REM Instalar dependencias
echo Instalando dependencias...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Fallo al instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas exitosamente
echo.

REM Mostrar menú
:menu
cls
echo.
echo ========================================
echo    CYBER-INVENTORY - Menu Principal
echo ========================================
echo.
echo Opciones disponibles:
echo 1 - Ejecutar servidor (desarrollo)
echo 2 - Ejecutar tests
echo 3 - Ejecutar tests con verbosidad
echo 4 - Mostrar documentación API
echo 5 - Limpiar cache de Python
echo 6 - Salir
echo.
set /p choice="Selecciona una opción (1-6): "

if "%choice%"=="1" goto run_server
if "%choice%"=="2" goto run_tests
if "%choice%"=="3" goto run_tests_verbose
if "%choice%"=="4" goto show_docs
if "%choice%"=="5" goto clean_cache
if "%choice%"=="6" goto exit_script

echo Opción inválida
timeout /t 1 /nobreak
goto menu

:run_server
echo.
echo Iniciando servidor Cyber-Inventory...
echo El servidor estará disponible en: http://localhost:8000
echo Documentación API: http://localhost:8000/docs
echo.
timeout /t 2 /nobreak
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
goto menu

:run_tests
echo.
echo Ejecutando tests...
pytest tests/
pause
goto menu

:run_tests_verbose
echo.
echo Ejecutando tests (verboso)...
pytest tests/ -v
pause
goto menu

:show_docs
echo.
echo La documentación interactiva está disponible en:
echo.
echo Swagger UI: http://localhost:8000/docs
echo ReDoc: http://localhost:8000/redoc
echo.
echo Asegúrate de que el servidor esté ejecutándose primero.
pause
goto menu

:clean_cache
echo.
echo Limpiando caché de Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q ".pytest_cache\" >nul 2>&1
echo [OK] Caché limpiado
timeout /t 1 /nobreak
goto menu

:exit_script
echo.
echo Para ejecutar el servidor manualmente:
echo     python -m uvicorn app.main:app --reload
echo.
echo Para ejecutar tests manualmente:
echo     pytest tests/ -v
echo.
echo ¡Hasta luego!
pause
endlocal
exit /b 0
