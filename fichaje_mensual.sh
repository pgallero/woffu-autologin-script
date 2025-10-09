#!/bin/bash

#================================================================
# Script para registrar fichajes de un mes completo en Woffu
# VERSIÓN 6.0 - Añadida comprobación de hora futura.
# Compara la hora de salida con la hora actual para máxima precisión.
#================================================================

# --- Configuración ---
YEAR="2025"
MONTH="10" # Mes a procesar (ej: 10 para octubre)
BASE_START_TIME="08:00:00"
BASE_END_TIME="15:00:00"
# --- Fin de la Configuración ---

# --- Función Auxiliar ---
seconds_to_hhmmss() {
  local total_seconds=$1
  local hours=$((total_seconds / 3600))
  local minutes=$(((total_seconds % 3600) / 60))
  local seconds=$((total_seconds % 60))
  printf "%02d:%02d:%02d" $hours $minutes $seconds
}

# --- Lógica Principal ---
IFS=':' read -r h m s <<< "$BASE_START_TIME"
BASE_START_SECONDS=$((10#$h * 3600 + 10#$m * 60 + 10#$s))

IFS=':' read -r h m s <<< "$BASE_END_TIME"
BASE_END_SECONDS=$((10#$h * 3600 + 10#$m * 60 + 10#$s))

DAYS_IN_MONTH=$(cal $MONTH $YEAR | awk 'NF {DAYS = $NF}; END {print DAYS}')
NOW_SECONDS=$(date +%s) # <-- NUEVA LÍNEA: Obtiene el timestamp actual exacto

echo "📅 Procesando fichajes para $MONTH/$YEAR..."
echo "=========================================="

for day in $(seq 1 $DAYS_IN_MONTH); do
  CURRENT_DATE=$(printf "%s-%s-%02d" $YEAR $MONTH $day)
  DAY_OF_WEEK=$(date -d "$CURRENT_DATE" +%u)

  if (( DAY_OF_WEEK < 6 )); then
    # Primero se generan las horas para poder compararlas
    START_OFFSET=$((RANDOM % 601 - 300))
    END_OFFSET=$((RANDOM % 601 - 300))

    RANDOM_START_SECONDS=$((BASE_START_SECONDS + START_OFFSET))
    RANDOM_END_SECONDS=$((BASE_END_SECONDS + END_OFFSET))

    RANDOM_START_TIME=$(seconds_to_hhmmss $RANDOM_START_SECONDS)
    RANDOM_END_TIME=$(seconds_to_hhmmss $RANDOM_END_SECONDS)

    # <-- LÓGICA MODIFICADA: Compara el timestamp de la hora de salida con el actual
    END_TIMESTAMP_SECONDS=$(date -d "$CURRENT_DATE $RANDOM_END_TIME" +%s)

    if (( END_TIMESTAMP_SECONDS < NOW_SECONDS )); then
      COMMAND="python3 woffu.py -d \"$CURRENT_DATE\" -s \"$RANDOM_START_TIME\" -e \"$RANDOM_END_TIME\""
      echo "Ejecutando para el día $CURRENT_DATE -> Entrada: $RANDOM_START_TIME | Salida: $RANDOM_END_TIME"

      # Comenta la siguiente línea para ejecutar el comando y no modificar Woffu
      eval $COMMAND
    else
      echo "Saltando fichaje de $CURRENT_DATE a las $RANDOM_END_TIME (aún no ha pasado)"
    fi
  else
    echo "Saltando día $CURRENT_DATE (Fin de semana)"
  fi
done

echo "=========================================="
echo "✅ Proceso completado."
