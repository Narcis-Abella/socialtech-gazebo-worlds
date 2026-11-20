#!/usr/bin/env bash
# Muestra un mapa de ocupación 2D en RViz2 (ROS 2 Jazzy: nav2_map_server, nav2_util, rviz2).
#   ./ver_mapa.sh                         mapa con muros y muebles
#   ./ver_mapa.sh casa_jose_solo_muros    solo muros
set -e
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; MAPA="${1:-casa_jose}"
[ -f "$AQUI/maps/$MAPA.yaml" ] || { echo "No existe maps/$MAPA.yaml"; exit 2; }
[ -n "${ROS_DISTRO:-}" ] || { set +u; source /opt/ros/jazzy/setup.bash; }
# El nodo se lanza directamente (no con 'ros2 run') para que la limpieza cierre el propio map_server:
# con 'ros2 run' solo se cerraba el envoltorio y map_server quedaba activo si RViz2 fallaba.
MS=; RV=
limpiar() {
  for p in $RV $MS; do kill -INT "$p" 2>/dev/null || true; done
  for p in $RV $MS; do wait "$p" 2>/dev/null || true; done
}
trap limpiar EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
"$(ros2 pkg prefix nav2_map_server)/lib/nav2_map_server/map_server" --ros-args -p yaml_filename:="$AQUI/maps/$MAPA.yaml" & MS=$!
sleep 3; ros2 run nav2_util lifecycle_bringup map_server
rviz2 -d "$AQUI/rviz/casa_jose.rviz" & RV=$!; wait "$RV"
