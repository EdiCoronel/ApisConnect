#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modifique esta línea según sea necesario para su administrador de paquetes (pip, poetry, etc.)
pip install -r requirements.txt

# Convertir archivos de activos estáticos
python manage.py collectstatic --no-input

# Aplicar cualquier migración de base de datos pendiente
python manage.py migrate