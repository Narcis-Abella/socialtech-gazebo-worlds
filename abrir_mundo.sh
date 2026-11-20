#!/usr/bin/env bash
# Abre el mundo de la casa en Gazebo Harmonic usando SOLO los archivos de esta carpeta (rutas relativas).
#   ./abrir_mundo.sh            -> Gazebo con ventana
#   ./abrir_mundo.sh --sin-gui  -> solo el servidor (sin ventana)
# En máquinas virtuales sin aceleración 3D: LIBGL_ALWAYS_SOFTWARE=1 ./abrir_mundo.sh
set -e
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export GZ_SIM_RESOURCE_PATH="$AQUI/models${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"
# Gazebo instalado con ROS 2 Jazzy (paquetes ros-jazzy-ros-gz): 'gz' solo está en el PATH tras cargar ROS
if ! command -v gz >/dev/null && [ -f /opt/ros/jazzy/setup.bash ]; then set +u; source /opt/ros/jazzy/setup.bash; fi
command -v gz >/dev/null || { echo "No encuentro 'gz': instala Gazebo Harmonic (ver README.md)"; exit 1; }
if [ "${1:-}" = "--sin-gui" ]; then exec gz sim -s -r "$AQUI/worlds/casa_jose.sdf"; else exec gz sim -r "$AQUI/worlds/casa_jose.sdf"; fi
