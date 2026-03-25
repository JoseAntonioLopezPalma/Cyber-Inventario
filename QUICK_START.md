# ⚡ QUICK START - Cyber-Inventory MVP

**Inicia el sistema en 5 minutos** ⏱️

---

## 🏃 Opción 1: Script Automatizado (MÁS FÁCIL)

### Windows
```bash
setup_windows.bat
```
Se abrirá un menú interactivo. Selecciona opción "1" para iniciar el servidor.

### Mac / Linux
```bash
chmod +x setup.sh
./setup.sh
```
Selecciona opción "1" para iniciar el servidor.

---

## 🏃 Opción 2: Manual (5 pasos)

### Paso 1: Crear Entorno Virtual
```bash
cd c:\Users\Candryl\Desktop\Proyecto
python -m venv venv
```

### Paso 2: Activar Entorno

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```
⏱️ Espera 1-2 minutos...

### Paso 4: Iniciar Servidor
```bash
python -m uvicorn app.main:app --reload
```

Verás:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Paso 5: Abre el Navegador
Dirígete a: **http://localhost:8000/**

---

## 🎮 ¡Ya Puedes Usar Cyber-Inventory!

### Funcionalidades Inmediatas

1. **📊 Dashboard** - Ve el estado del inventario
2. **➕ Crear Ítem** - Agrega nuevo hardware
3. **📦 Inventario** - Visualiza todos los ítems
4. **🔍 Buscar** - Encuentra productos

### URLs Importantes

| URL | Descripción |
|-----|------------|
| http://localhost:8000/ | 🎨 **Frontend** |
| http://localhost:8000/docs | 📚 **Swagger API** |
| http://localhost:8000/redoc | 📖 **ReDoc** |

---

## 🧪 Ejecutar Tests (En otra terminal)

Con el servidor en ejecución, abre **otra terminal** y:

```bash
# Activar venv (misma carpeta)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Ejecutar tests
pytest tests/ -v
```

Verás:
```
================== 80+ tests passed in 2.5s ==================
```

---

## 🎯 Ejemplo de Flujo de Uso

1. **Abre**: http://localhost:8000/
2. **Crea un ítem**: ➕ Crear Ítem
   - Nombre: "Intel Core i9-13900K"
   - Categoría: Microprocesadores
   - Stock: 10
   - Precio: 689.99
3. **Desde Inventario**:
   - Haz click en botón "+1" para aumentar stock
   - O "-1" para vender 1 unidad
4. **Busca** en 🔍 Buscar
5. **Edita** haciendo click en "Editar"

---

## 📊 Dashboard en Tiempo Real

El dashboard se actualiza automáticamente cada 5 segundos mostrando:
- **Total de Ítems** en inventario
- **Valor Total** de todo el inventario en USD

---

## 🛑 Detener el Servidor

En la terminal donde corre el servidor:
```
Presiona: Ctrl + C
```

---

## ❓ ¿Problemas?

### Error: "ModuleNotFoundError: No module named 'app'"
```bash
# Asegúrate de estar en la carpeta correcta
cd c:\Users\Candryl\Desktop\Proyecto
python -m uvicorn app.main:app --reload
```

### Error: "Address already in use :8000"
```bash
# Usa otro puerto
python -m uvicorn app.main:app --reload --port 8001
```

### Error: Tests fallan
```bash
pip install -r requirements.txt --force-reinstall
pytest tests/ --cache-clear
```

---

## 📚 Documentación Completa

Lee estos archivos para más detalles:

1. **[README.md](README.md)** - Guía completa
2. **[RESUMEN_IMPLEMENTACION.md](RESUMEN_IMPLEMENTACION.md)** - Qué se implementó
3. **Swagger UI** (`/docs`) - API interactiva

---

## ✅ Próximas Acciones

- [ ] Crear tu primer ítem
- [ ] Agregar 5+ productos
- [ ] Probar búsqueda
- [ ] Ejecutar tests
- [ ] Leer documentación Swagger
- [ ] Explorar el código (está bien comentado)

---

## 🚀 ¡Listo!

El sistema está completamente funcional, probado y documentado.

**Tiempo hasta tener todo corriendo: 5 minutos**

¿Preguntas? Revisa [README.md](README.md) o los comentarios en el código.

---

🎉 **¡Disfruta del MVP!** 🎉
