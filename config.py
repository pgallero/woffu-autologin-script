# Configuración para Woffu Autologin
# Este archivo contiene todas las configuraciones del sistema

# === CONFIGURACIÓN PRINCIPAL ===
YEAR = 2025
MONTH = 10  # Mes a procesar (1-12)

# === HORARIOS BASE ===
BASE_START_TIME = "08:00:00"  # Hora de entrada base (HH:MM:SS)
BASE_END_TIME = "15:00:00"    # Hora de salida base (HH:MM:SS)

# === VARIACIÓN ALEATORIA ===
# Variación máxima en segundos (±)
# 300 segundos = ±5 minutos
RANDOM_VARIATION_SECONDS = 300

# === OPCIONES DE PROCESAMIENTO ===
SKIP_WEEKENDS = True          # Saltar fines de semana automáticamente
SKIP_FUTURE_DATES = True      # Saltar fechas donde la hora de salida aún no ha pasado

# === ARCHIVOS DEL SISTEMA ===
WOFFU_SCRIPT = "woffu.py"     # Nombre del script principal de Woffu
DATA_FILE = "data.json"       # Archivo de datos de usuario

# === CONFIGURACIÓN DE SALIDA ===
SHOW_PROGRESS = True          # Mostrar progreso detallado
SHOW_STATISTICS = True        # Mostrar estadísticas al final
USE_COLORS = True             # Usar colores en la salida (si está disponible)
