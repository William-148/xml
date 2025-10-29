# Proyecto XML Cloud

Este repositorio contiene dos aplicaciones independientes:

- `program1/` → Proyecto Django  
- `service2/` → Proyecto Flask

Cada uno tiene su propio entorno virtual y se ejecuta por separado.

## Requisitos

- Python 3.10 o superior  
- pip  
- Git (opcional)

## Cómo ejecutar los proyectos

### 1. Django (`program1/`)
Todo el proceso se hace dentro de la carpeta `program1/`.

Crear entorno virtual (solo la primera vez):
```bash
python -m venv venv
```

Activar entorno virtual (cada vez que cierres y vuelvas a abrir la terminal):

Linux/macOS:
```bash
source venv/bin/activate
```

Windows:
```bash
.\env\Scripts\activar
```

Instalar dependencias (solo la primera vez):
```bash
pip install -r requirements.txt
```

Ejecutar el servidor:
```bash
python manage.py runserver
```

Esto iniciará el servidor en http://localhost:8000

### 2. Flask (`service2/`)
Todo el proceso se hace dentro de la carpeta `service2/`.

Crear entorno virtual (solo la primera vez):
```bash
python -m venv venv
```

Activar entorno virtual (cada vez que cierres y vuelvas a abrir la terminal):
Linux/macOS:
```bash
source venv/bin/activate
```

Windows:
```bash
.\env\Scripts\activate
```

Instalar dependencias (solo la primera vez):
```bash
pip install -r requirements.txt
```

Ejecutar la aplicación:
```bash
python app.py
```

Esto iniciará el servidor en http://localhost:5000

## Estructura del repositorio

.
├── program1/            # Proyecto Django
│   └── venv/            # Entorno virtual de Django
├── service2/            # Proyecto Flask
│   └── venv/            # Entorno virtual de Flask

## Notas

- Asegúrate de activar el entorno correcto antes de ejecutar cada proyecto.
- Puedes instalar las dependencias con pip install -r requirements.txt si el archivo está disponible en cada carpeta.
- Ambos proyectos se ejecutan de forma independiente, pero pueden comunicarse.

