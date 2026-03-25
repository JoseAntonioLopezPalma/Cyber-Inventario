#!/bin/bash

# Script de Instalación y Ejecución para Cyber-Inventory en Linux/Mac
# Este script automatiza la instalación y puesta en marcha del MVP

set -e

# Colores para el output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones útiles
print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo
echo "========================================"
echo "  CYBER-INVENTORY - Setup Script"
echo "========================================"
echo

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado"
    echo "Instala Python desde: https://www.python.org/"
    exit 1
fi

print_success "Python detectado"
python3 --version
echo

# Crear entorno virtual
print_info "Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Entorno virtual creado"
else
    print_success "Entorno virtual ya existe"
fi
echo

# Activar entorno virtual
print_info "Activando entorno virtual..."
source venv/bin/activate
print_success "Entorno virtual activado"
echo

# Instalar dependencias
print_info "Instalando dependencias..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    print_success "Dependencias instaladas"
else
    print_error "Fallo al instalar dependencias"
    exit 1
fi
echo

# Mostrar menú
show_menu() {
    echo
    echo "========================================"
    echo "  CYBER-INVENTORY - Menu Principal"
    echo "========================================"
    echo
    echo "Opciones disponibles:"
    echo "1 - Ejecutar servidor (desarrollo)"
    echo "2 - Ejecutar tests"
    echo "3 - Ejecutar tests con verbosidad"
    echo "4 - Ejecutar tests con cobertura"
    echo "5 - Mostrar documentación API"
    echo "6 - Limpiar caché de Python"
    echo "7 - Salir"
    echo
    read -p "Selecciona una opción (1-7): " choice
}

run_server() {
    echo
    echo "Iniciando servidor Cyber-Inventory..."
    echo "El servidor estará disponible en: http://localhost:8000"
    echo "Documentación API: http://localhost:8000/docs"
    echo
    sleep 2
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

run_tests() {
    echo
    echo "Ejecutando tests..."
    pytest tests/
    read -p "Presiona Enter para continuar..."
}

run_tests_verbose() {
    echo
    echo "Ejecutando tests (verboso)..."
    pytest tests/ -v
    read -p "Presiona Enter para continuar..."
}

run_tests_coverage() {
    echo
    echo "Ejecutando tests con cobertura..."
    pip install -q pytest-cov
    pytest tests/ --cov=app --cov-report=html
    print_success "Reporte de cobertura generado en htmlcov/index.html"
    read -p "Presiona Enter para continuar..."
}

show_docs() {
    echo
    echo "La documentación interactiva está disponible en:"
    echo
    echo "Swagger UI: http://localhost:8000/docs"
    echo "ReDoc: http://localhost:8000/redoc"
    echo
    echo "Asegúrate de que el servidor esté ejecutándose primero."
    read -p "Presiona Enter para continuar..."
}

clean_cache() {
    echo
    echo "Limpiando caché de Python..."
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
    print_success "Caché limpiado"
    sleep 1
}

# Loop del menú
while true; do
    show_menu
    case $choice in
        1) run_server ;;
        2) run_tests ;;
        3) run_tests_verbose ;;
        4) run_tests_coverage ;;
        5) show_docs ;;
        6) clean_cache ;;
        7) 
            echo
            echo "Para ejecutar el servidor manualmente:"
            echo "    python -m uvicorn app.main:app --reload"
            echo
            echo "Para ejecutar tests manualmente:"
            echo "    pytest tests/ -v"
            echo
            echo "¡Hasta luego!"
            exit 0
            ;;
        *) 
            print_error "Opción inválida"
            sleep 1
            ;;
    esac
done
