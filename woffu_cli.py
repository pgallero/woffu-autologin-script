#!/usr/bin/env python3
"""
Woffu Autologin - Script Unificado
Versión 8.0 - Multiplataforma con configuración externa

Este script proporciona dos funcionalidades principales:
1. Fichaje individual para un día específico
2. Fichaje mensual para procesar un mes completo

Funciona de manera idéntica en Windows, macOS y Linux.
"""

import sys
import os
import subprocess
import calendar
import random
import argparse
from typing import List, Dict, Tuple, Optional
from datetime import datetime, date
from pathlib import Path

# Importar configuración
try:
    from config import *
except ImportError:
    print("❌ Error: No se encontró el archivo config.py")
    print("   Asegúrate de que config.py esté en el mismo directorio")
    sys.exit(1)

# Importar la función de woffu
try:
    from woffu import woffu_file_entry, woffu_file_entry_multi
    WOFFU_AVAILABLE = True
except ImportError:
    print("⚠️ Advertencia: No se pudo importar woffu.py, usando subprocess como respaldo")
    WOFFU_AVAILABLE = False


class WoffuAutologin:
    """Clase principal para manejar el autologin de Woffu"""
    
    def __init__(self):
        self.now = datetime.now()
        self.script_dir = Path(__file__).parent
        
    def _print_message(self, message, msg_type="info"):
        """Imprime mensajes con formato consistente"""
        if not SHOW_PROGRESS:
            return
            
        icons = {
            "success": "[OK]",
            "error": "[ERROR]", 
            "warning": "[WARN]",
            "info": "[INFO]",
            "progress": "[EXEC]",
            "skip": "[SKIP]",
            "stats": "[STAT]"
        }
        
        icon = icons.get(msg_type, "[???]")
        print(f"{icon} {message}")
    
    def _time_to_seconds(self, time_str):
        """Convierte una cadena de tiempo HH:MM:SS a segundos desde medianoche"""
        try:
            time_obj = datetime.strptime(time_str, "%H:%M:%S")
            return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
        except ValueError:
            raise ValueError(f"Formato de tiempo inválido: {time_str}. Use HH:MM:SS")
    
    def _seconds_to_time(self, seconds):
        """Convierte segundos desde medianoche a formato HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _is_weekday(self, year, month, day):
        """Verifica si un día es día laboral (lunes a viernes)"""
        date_obj = date(year, month, day)
        return date_obj.weekday() < 5  # 0-6, donde 0 es lunes y 6 es domingo
    
    def _get_days_in_month(self, year, month):
        """Obtiene el número de días en un mes específico"""
        return calendar.monthrange(year, month)[1]
    
    def _generate_random_times(self, base_start, base_end):
        """Genera horarios aleatorios basados en la configuración"""
        base_start_seconds = self._time_to_seconds(base_start)
        base_end_seconds = self._time_to_seconds(base_end)
        
        # Aplicar variación aleatoria
        start_offset = random.randint(-RANDOM_VARIATION_SECONDS, RANDOM_VARIATION_SECONDS)
        end_offset = random.randint(-RANDOM_VARIATION_SECONDS, RANDOM_VARIATION_SECONDS)
        
        random_start_seconds = base_start_seconds + start_offset
        random_end_seconds = base_end_seconds + end_offset
        
        # Asegurar que los tiempos estén dentro del día (0-86399 segundos)
        random_start_seconds = max(0, min(86399, random_start_seconds))
        random_end_seconds = max(0, min(86399, random_end_seconds))
        
        # Asegurar que la hora de salida sea posterior a la de entrada
        if random_end_seconds <= random_start_seconds:
            random_end_seconds = random_start_seconds + random.randint(3600, 7200)  # +1-2 horas
            random_end_seconds = min(86399, random_end_seconds)
        
        return (self._seconds_to_time(random_start_seconds), 
                self._seconds_to_time(random_end_seconds))
    
    def _is_future_time(self, year, month, day, end_time):
        """Verifica si la hora de salida está en el futuro"""
        if not SKIP_FUTURE_DATES:
            return False
            
        try:
            end_datetime = datetime.strptime(f"{year}-{month:02d}-{day:02d} {end_time}", 
                                           "%Y-%m-%d %H:%M:%S")
            return end_datetime > self.now
        except ValueError:
            self._print_message(f"Error al parsear la fecha/hora: {year}-{month:02d}-{day:02d} {end_time}", "warning")
            return True  # En caso de error, asumir que es futuro para evitar ejecución
    
    def _verify_woffu_script(self):
        """Verifica que el script woffu.py existe"""
        woffu_path = self.script_dir / WOFFU_SCRIPT
        if not woffu_path.exists():
            self._print_message(f"No se encontró {WOFFU_SCRIPT} en el directorio actual", "error")
            self._print_message(f"Directorio actual: {self.script_dir}", "error")
            return False
        return True
    
    def execute_single_filing(self, filing_date, start_time, end_time, dry_run=False):
        """
        Función 1: Ejecuta un fichaje individual para un día específico
        
        Args:
            filing_date (str): Fecha en formato YYYY-MM-DD
            start_time (str): Hora de entrada en formato HH:MM:SS
            end_time (str): Hora de salida en formato HH:MM:SS
            dry_run (bool): Si True, solo muestra qué se ejecutaría sin hacerlo
        
        Returns:
            bool: True si la ejecución fue exitosa, False en caso contrario
        """
        if not self._verify_woffu_script():
            return False
        
        if dry_run:
            command = [sys.executable, WOFFU_SCRIPT, "-d", filing_date, "-s", start_time, "-e", end_time]
            self._print_message(f"[DRY RUN] Comando que se ejecutaría: {' '.join(command)}", "info")
            return True
        
        # Usar importación directa si está disponible (más eficiente)
        if WOFFU_AVAILABLE:
            try:
                success = woffu_file_entry(filing_date, start_time, end_time, DATA_FILE)
                if success:
                    self._print_message(f"Fichaje ejecutado correctamente para {filing_date}", "success")
                else:
                    self._print_message(f"Error al ejecutar fichaje para {filing_date}", "error")
                return success
            except Exception as e:
                self._print_message(f"Error durante el fichaje para {filing_date}: {e}", "error")
                return False
        
        # Respaldo usando subprocess
        else:
            command = [sys.executable, WOFFU_SCRIPT, "-d", filing_date, "-s", start_time, "-e", end_time]
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=self.script_dir)
                self._print_message(f"Fichaje ejecutado correctamente para {filing_date}", "success")
                if result.stdout and SHOW_PROGRESS:
                    print(f"   Salida: {result.stdout.strip()}")
                return True
            except subprocess.CalledProcessError as e:
                self._print_message(f"Error al ejecutar fichaje para {filing_date}: {e}", "error")
                if e.stderr:
                    print(f"   Error: {e.stderr.strip()}")
                return False
            except FileNotFoundError:
                self._print_message(f"No se encontró {WOFFU_SCRIPT} o Python", "error")
                return False
    
    def _parse_interval(self, interval_str: str) -> Tuple[str, str]:
        """Parses a single time interval start-end (HH:MM or HH:MM:SS). Returns normalized HH:MM:SS.
        Raises ValueError on invalid format."""
        if '-' not in interval_str:
            raise ValueError(f"Intervalo inválido '{interval_str}'. Debe ser start-end")
        start_raw, end_raw = interval_str.split('-', 1)
        def norm(t: str) -> str:
            parts = t.strip().split(':')
            if len(parts) == 1:
                raise ValueError(f"Hora inválida '{t}'. Use HH:MM o HH:MM:SS")
            if len(parts) == 2:
                h, m = parts
                s = '00'
            elif len(parts) == 3:
                h, m, s = parts
            else:
                raise ValueError(f"Hora inválida '{t}'")
            h = int(h); m = int(m); s = int(s)
            if not (0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60):
                raise ValueError(f"Hora fuera de rango '{t}'")
            return f"{h:02d}:{m:02d}:{s:02d}"
        start = norm(start_raw)
        end = norm(end_raw)
        if start >= end:
            raise ValueError(f"Intervalo inválido {start}-{end}: inicio debe ser < fin")
        return start, end

    def _parse_same_schedule(self, schedule_str: str) -> List[Tuple[str, str]]:
        """Parses a string like '08:00-14:30,15:00-17:00' into list of intervals."""
        intervals: List[Tuple[str, str]] = []
        for chunk in schedule_str.split(','):
            chunk = chunk.strip()
            if not chunk:
                continue
            intervals.append(self._parse_interval(chunk))
        if not intervals:
            raise ValueError("Debe especificar al menos un intervalo en --same-schedule")
        return intervals

    def _parse_weekly_schedule(self, weekly_str: str) -> Dict[int, List[Tuple[str, str]]]:
        """Parses weekly schedule like:
        L=08:00-14:30,15:00-17:00;V=08:00-14:00  (Soporte días: L M X J V S D)
        Returns dict weekday_index -> list[(start,end)] where Monday=0.
        """
        day_map = {"L":0, "M":1, "X":2, "J":3, "V":4, "S":5, "D":6}
        result: Dict[int, List[Tuple[str, str]]] = {}
        for segment in weekly_str.split(';'):
            segment = segment.strip()
            if not segment:
                continue
            if '=' not in segment:
                raise ValueError(f"Segmento semanal inválido '{segment}'. Use DIA=intervalos")
            day_code, intervals_str = segment.split('=',1)
            day_code = day_code.strip().upper()
            if day_code not in day_map:
                raise ValueError(f"Código de día inválido '{day_code}'. Use L,M,X,J,V,S,D")
            intervals = self._parse_same_schedule(intervals_str)
            result[day_map[day_code]] = intervals
        if not result:
            raise ValueError("Debe especificar al menos un día en --weekly-schedule")
        return result

    def execute_monthly_filing(self, year=None, month=None, start_time=None, end_time=None, 
                             skip_weekends=None, dry_run=False,
                             same_schedule: Optional[str]=None,
                             weekly_schedule: Optional[str]=None):
        """
        Función 2: Procesa fichajes para un mes completo
        
        Args:
            year (int): Año a procesar (por defecto desde config)
            month (int): Mes a procesar (por defecto desde config)
            start_time (str): Hora base de entrada (por defecto desde config)
            end_time (str): Hora base de salida (por defecto desde config)
            skip_weekends (bool): Saltar fines de semana (por defecto desde config)
            dry_run (bool): Modo de prueba sin ejecución real
        
        Returns:
            dict: Estadísticas del procesamiento
        """
        # Usar valores por defecto de la configuración si no se especifican
        year = year or YEAR
        month = month or MONTH
        start_time = start_time or BASE_START_TIME
        end_time = end_time or BASE_END_TIME
        skip_weekends = skip_weekends if skip_weekends is not None else SKIP_WEEKENDS
        
        if not self._verify_woffu_script():
            return {"success": 0, "skipped": 0, "errors": 0}
        
        days_in_month = self._get_days_in_month(year, month)
        
        # Mostrar información inicial
        print("=" * 60)
        self._print_message(f"Procesando fichajes para {month:02d}/{year}", "info")
        # Determinar estrategia de horarios
        weekly_intervals: Dict[int, List[Tuple[str,str]]] = {}
        base_intervals: List[Tuple[str,str]] = []
        strategy = 'simple'
        try:
            if weekly_schedule:
                weekly_intervals = self._parse_weekly_schedule(weekly_schedule)
                strategy = 'weekly'
            elif same_schedule:
                base_intervals = self._parse_same_schedule(same_schedule)
                strategy = 'same'
            else:
                base_intervals = [(start_time, end_time)]
        except ValueError as ve:
            self._print_message(f"Error en horarios: {ve}", "error")
            return {"success":0,"skipped":0,"errors":1}

        if strategy == 'simple':
            self._print_message(f"Horario base simple: {start_time} - {end_time}", "info")
        elif strategy == 'same':
            self._print_message(f"Horario uniforme ({len(base_intervals)} intervalo(s)): {', '.join([f"{a}-{b}" for a,b in base_intervals])}", "info")
        else:
            desc = []
            rev_day = {0:'L',1:'M',2:'X',3:'J',4:'V',5:'S',6:'D'}
            for d, ints in sorted(weekly_intervals.items()):
                desc.append(f"{rev_day[d]}: {', '.join([f"{a}-{b}" for a,b in ints])}")
            self._print_message("Horario semanal → " + " | ".join(desc), "info")
        self._print_message(f"Variación aleatoria: ±{RANDOM_VARIATION_SECONDS//60} minutos", "info")
        if dry_run:
            self._print_message("MODO DRY RUN - No se ejecutarán los comandos realmente", "warning")
        print("=" * 60)
        
        stats = {"success": 0, "skipped": 0, "errors": 0}
        
        for day in range(1, days_in_month + 1):
            current_date = f"{year}-{month:02d}-{day:02d}"
            
            # Verificar si es día laboral
            if skip_weekends and not self._is_weekday(year, month, day):
                self._print_message(f"Saltando {current_date} (Fin de semana)", "skip")
                stats["skipped"] += 1
                continue
            
            # Seleccionar intervalos para el día
            date_obj = date(year, month, day)
            day_of_week = date_obj.weekday()  # Monday=0
            if strategy == 'weekly':
                if day_of_week in weekly_intervals:
                    intervals_today = weekly_intervals[day_of_week]
                else:
                    self._print_message(f"Sin horario configurado para {current_date} (día {day_of_week}), se omite", "skip")
                    stats["skipped"] += 1
                    continue
            else:
                intervals_today = base_intervals

            # Generar variación para cada intervalo y construir lista consolidada
            randomized_intervals = []
            for (base_start_i, base_end_i) in intervals_today:
                if RANDOM_VARIATION_SECONDS > 0:
                    r_start, r_end = self._generate_random_times(base_start_i, base_end_i)
                else:
                    r_start, r_end = base_start_i, base_end_i
                if self._is_future_time(year, month, day, r_end):
                    self._print_message(f"Saltando intervalo {r_start}-{r_end} de {current_date} (futuro)", "skip")
                    continue
                randomized_intervals.append((r_start, r_end))

            if not randomized_intervals:
                stats["skipped"] += 1
                continue

            # Ordenar y validar no solapamiento
            randomized_intervals.sort(key=lambda x: x[0])
            valid = True
            for i in range(1, len(randomized_intervals)):
                if randomized_intervals[i-1][1] > randomized_intervals[i][0]:
                    self._print_message(f"Intervalos solapados detectados en {current_date}: {randomized_intervals[i-1]} y {randomized_intervals[i]}", "error")
                    stats["errors"] += 1
                    valid = False
                    break
            if not valid:
                continue

            # Si cualquier fin cae en futuro, omitir todo el día (consistente)
            if any(self._is_future_time(year, month, day, end) for _, end in randomized_intervals):
                self._print_message(f"Saltando {current_date} (intervalo con salida futura)", "skip")
                stats["skipped"] += 1
                continue

            interval_desc = ", ".join([f"{a}-{b}" for a,b in randomized_intervals])
            self._print_message(f"Procesando {current_date} -> {interval_desc}", "progress")

            if dry_run:
                # Mostrar los comandos que se ejecutarían
                for s,e in randomized_intervals:
                    cmd = [sys.executable, WOFFU_SCRIPT, '-d', current_date, '-s', s, '-e', e]
                    self._print_message(f"[DRY RUN] Comando que se ejecutaría: {' '.join(cmd)}", "info")
                stats["success"] += 1
            else:
                if WOFFU_AVAILABLE and len(randomized_intervals) > 1:
                    # Usar llamada múltiple
                    try:
                        if woffu_file_entry_multi(current_date, randomized_intervals, DATA_FILE):
                            stats["success"] += 1
                        else:
                            stats["errors"] += 1
                    except Exception as e:
                        self._print_message(f"Error en fichaje múltiple {current_date}: {e}", "error")
                        stats["errors"] += 1
                else:
                    # Fallback a fichajes individuales
                    day_ok = True
                    for s,e in randomized_intervals:
                        if not self.execute_single_filing(current_date, s, e, dry_run):
                            day_ok = False
                    if day_ok:
                        stats["success"] += 1
                    else:
                        stats["errors"] += 1
        
        # Mostrar estadísticas finales
        if SHOW_STATISTICS:
            print("=" * 60)
            self._print_message("Proceso completado", "success")
            self._print_message(f"Fichajes procesados: {stats['success']}", "stats")
            self._print_message(f"Días saltados: {stats['skipped']}", "stats")
            if stats["errors"] > 0:
                self._print_message(f"Errores: {stats['errors']}", "error")
            print("=" * 60)
        
        return stats


def main():
    """Función principal con interfaz de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Woffu CLI - Interfaz de Línea de Comandos Multiplataforma",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  
FICHAJE INDIVIDUAL:
  python woffu_cli.py single -d "2025-10-15" -s "08:30:00" -e "15:30:00"
  python woffu_cli.py single -d "2025-10-15" -s "08:30:00" -e "15:30:00" --dry-run

FICHAJE MENSUAL:
  python woffu_cli.py monthly                                    (usa config por defecto)
  python woffu_cli.py monthly --year 2025 --month 11             (noviembre 2025)
  python woffu_cli.py monthly --start-time "09:00:00" --end-time "17:00:00"
  python woffu_cli.py monthly --dry-run                          (modo de prueba)
  python woffu_cli.py monthly --include-weekends                 (incluir fines de semana)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Subcomando para fichaje individual
    single_parser = subparsers.add_parser('single', help='Fichaje individual para un día específico')
    single_parser.add_argument('-d', '--date', required=True, help='Fecha en formato YYYY-MM-DD')
    single_parser.add_argument('-s', '--start-time', required=True, help='Hora de entrada (HH:MM:SS)')
    single_parser.add_argument('-e', '--end-time', required=True, help='Hora de salida (HH:MM:SS)')
    single_parser.add_argument('--dry-run', action='store_true', help='Modo de prueba sin ejecución')
    
    # Subcomando para fichaje mensual
    monthly_parser = subparsers.add_parser('monthly', help='Fichaje mensual completo')
    monthly_parser.add_argument('--year', type=int, help=f'Año a procesar (por defecto: {YEAR})')
    monthly_parser.add_argument('--month', type=int, help=f'Mes a procesar (por defecto: {MONTH})')
    monthly_parser.add_argument('--start-time', help=f'Hora base de entrada (por defecto: {BASE_START_TIME})')
    monthly_parser.add_argument('--end-time', help=f'Hora base de salida (por defecto: {BASE_END_TIME})')
    monthly_parser.add_argument('--include-weekends', action='store_true', help='Incluir fines de semana')
    monthly_parser.add_argument('--dry-run', action='store_true', help='Modo de prueba sin ejecución')
    # Nuevos flags de horarios avanzados
    monthly_parser.add_argument('--same-schedule', help='Mismos intervalos para todos los días laborables. Ej: "08:00-14:30,15:00-17:00"')
    monthly_parser.add_argument('--weekly-schedule', help='Horarios por día. Ej: "L=08:00-14:30,15:00-17:00;V=08:00-14:00"')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Crear instancia del autologin
    woffu = WoffuAutologin()
    
    try:
        if args.command == 'single':
            # Validar formato de fecha
            try:
                datetime.strptime(args.date, "%Y-%m-%d")
            except ValueError:
                print("[ERROR] Error: Formato de fecha inválido. Use YYYY-MM-DD")
                sys.exit(1)
            
            # Ejecutar fichaje individual
            success = woffu.execute_single_filing(
                args.date, 
                args.start_time, 
                args.end_time, 
                args.dry_run
            )
            sys.exit(0 if success else 1)
            
        elif args.command == 'monthly':
            # Validaciones para fichaje mensual
            if args.month and not (1 <= args.month <= 12):
                print("[ERROR] Error: El mes debe estar entre 1 y 12")
                sys.exit(1)
            
            if args.year and not (2020 <= args.year <= 2030):
                print("[ERROR] Error: El año debe estar entre 2020 y 2030")
                sys.exit(1)
            
            # Ejecutar fichaje mensual
            stats = woffu.execute_monthly_filing(
                year=args.year,
                month=args.month,
                start_time=args.start_time,
                end_time=args.end_time,
                skip_weekends=not args.include_weekends,
                dry_run=args.dry_run,
                same_schedule=args.same_schedule,
                weekly_schedule=args.weekly_schedule
            )
            
            # Código de salida basado en resultados
            if stats["errors"] > 0:
                sys.exit(1)
            else:
                sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n[STOP] Proceso interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
