# Woffu Autologin - Script Unificado

Este proyecto proporciona una solución **completamente unificada y multiplataforma** para automatizar el fichaje en Woffu. Funciona de manera idéntica en Windows, macOS y Linux.

---

## 🎯 Características Principales

- ✅ **Completamente multiplataforma** - Idéntico funcionamiento en todos los sistemas operativos
- ✅ **Dos funciones principales** - Fichaje individual y fichaje mensual
- ✅ **Configuración externa** - Todas las configuraciones en un archivo separado
- ✅ **Sin dependencias del sistema** - Solo Python puro
- ✅ **Interfaz unificada** - Una sola forma de usar en todos los sistemas

---

## 🛠️ Instalación

1. **Instalar Python 3.6+**
   ```bash
   # Verificar que Python está instalado
   python --version
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar datos de usuario** (primera ejecución)
   
   El script `woffu.py` te pedirá tus credenciales la primera vez y las guardará en `data.json`:
   ```json
   {
     "username": "<TU USUARIO WOFFU>",
     "password": "<TU CONTRASEÑA>",
     "user_id": <TU ID DE USUARIO>,
     "company_id": <ID DE LA EMPRESA>,
     "company_country": "<PAÍS DE LA EMPRESA>",
     "company_subdivision": "<REGIÓN>",
     "domain": "<DOMINIO WOFFU>",
     "woffu_url": "<URL DE WOFFU>"
   }
   ```

---

## ⚙️ Configuración

Todas las configuraciones están en el archivo `config.py`. Edítalo según tus necesidades:

---

## 🚀 Uso

### Función 1: Fichaje Individual

Para fichar un día específico:

```bash
# Fichaje básico
python woffu_cli.py single -d "2025-10-15" -s "08:30:00" -e "15:30:00"

# Modo de prueba (no ejecuta realmente)
python woffu_cli.py single -d "2025-10-15" -s "08:30:00" -e "15:30:00" --dry-run
```

### Función 2: Fichaje Mensual

Para procesar un mes completo:

```bash
# Usar configuración por defecto
python woffu_cli.py monthly

# Personalizar parámetros
python woffu_cli.py monthly --year 2025 --month 11

# Cambiar horarios
python woffu_cli.py monthly --start-time "09:00:00" --end-time "17:00:00"

# Incluir fines de semana
python woffu_cli.py monthly --include-weekends

# Modo de prueba
python woffu_cli.py monthly --dry-run

# Combinación de opciones
python woffu_cli.py monthly --year 2025 --month 12 --start-time "09:00:00" --end-time "17:30:00" --dry-run
```

### 🆕 Función 2B: Fichaje Mensual con Horarios Avanzados

**Horario Uniforme (con descansos):**
```bash
# Mismo horario todos los días: mañana + tarde con descanso
python woffu_cli.py monthly --same-schedule "08:00-14:30,15:00-17:00"

# Solo horario de mañana
python woffu_cli.py monthly --same-schedule "08:00-16:00"

# Tres bloques (mañana, mediodía, tarde)
python woffu_cli.py monthly --same-schedule "08:00-12:00,13:00-15:00,16:00-18:00"
```

**Horario por Días de la Semana:**
```bash
# Lunes completo, Viernes solo mañana
python woffu_cli.py monthly --weekly-schedule "L=08:00-14:30,15:00-17:00;V=08:00-14:00"

# Horarios diferentes cada día
python woffu_cli.py monthly --weekly-schedule "L=09:00-17:00;M=08:00-16:00;X=08:30-16:30;J=09:00-17:00;V=08:00-15:00"

# Incluir sábados
python woffu_cli.py monthly --weekly-schedule "L=08:00-16:00;S=10:00-14:00" --include-weekends
```

**Códigos de Días:**
- `L` = Lunes
- `M` = Martes  
- `X` = Miércoles
- `J` = Jueves
- `V` = Viernes
- `S` = Sábado
- `D` = Domingo

### Ver ayuda

```bash
# Ayuda general
python woffu_cli.py --help

# Ayuda específica
python woffu_cli.py single --help
python woffu_cli.py monthly --help
```

### 🔧 Ejemplos Avanzados

```bash
# Probar horarios antes de aplicar (RECOMENDADO)
python woffu_cli.py monthly --same-schedule "08:00-14:30,15:00-17:00" --dry-run

# Horario intensivo lunes-jueves, viernes corto
python woffu_cli.py monthly --weekly-schedule "L=08:00-14:30,15:00-17:00;M=08:00-14:30,15:00-17:00;X=08:00-14:30,15:00-17:00;J=08:00-14:30,15:00-17:00;V=08:00-14:00"

# Aplicar solo a diciembre 2025
python woffu_cli.py monthly --year 2025 --month 12 --same-schedule "09:00-17:00"
```

---

## 🌟 Ventajas de la Versión Unificada

### ✅ Simplicidad
- **Un solo script** para todo
- **Una sola forma de usar** en todos los sistemas operativos
- **Sin scripts auxiliares** específicos del sistema

### ✅ Configuración Externa
- **Archivo `config.py`** con todas las configuraciones
- **Fácil personalización** sin tocar el código principal
- **Configuraciones centralizadas**

### ✅ Funcionalidad Completa
- **Fichaje individual** para días específicos
- **Fichaje mensual** con lógica inteligente
- **🆕 Horarios múltiples** con descansos y pausas
- **🆕 Configuración semanal** diferente por día
- **Variación aleatoria** configurable
- **Salto automático** de fines de semana y fechas futuras

### ✅ Robustez
- **Manejo de errores** completo
- **Validaciones** de entrada y solapamiento
- **Modo dry-run** para pruebas
- **Estadísticas detalladas**
- **🆕 Optimización multi-intervalo** en una sola llamada API

---

## 📁 Estructura de Archivos

```
woffu-autologin/
├── woffu_cli.py         # 🎯 Script principal CLI
├── config.py            # ⚙️ Configuraciones centralizadas
├── woffu.py            # 🔧 Core de Woffu (refactorizado y limpio)
├── data.json           # 📄 Datos de usuario (se crea automáticamente)
├── requirements.txt    # 📦 Dependencias de Python
└── README.md          # 📚 Esta documentación
```

### ✨ Arquitectura Final

#### 🎯 **woffu_cli.py** - Interfaz de Línea de Comandos
- Interfaz CLI completa y profesional
- Gestión de las dos funciones principales (single/monthly)
- Importación directa de `woffu.py` para máxima eficiencia
- Lógica inteligente de procesamiento y validaciones

#### ⚙️ **config.py** - Centro de Configuración
- Todas las configuraciones en un solo lugar
- Fácil personalización sin tocar código
- Configuraciones documentadas y explicadas

#### 🔧 **woffu.py** - Motor de Fichaje
- Core simplificado y refactorizado
- Función `woffu_file_entry()` para uso programático
- Eliminada lógica obsoleta de argumentos
- Compatible con llamadas directas e importación

### 🔄 Cambios vs Versión Original

| Antes | Después |
|-------|---------|
| ❌ Scripts específicos por OS | ✅ Un solo script multiplataforma |
| ❌ Configuración hardcodeada | ✅ Archivo de configuración externo |
| ❌ Dependencias del sistema | ✅ Solo Python puro |
| ❌ Múltiples archivos auxiliares | ✅ Arquitectura limpia y minimal |
| ❌ Lógica duplicada | ✅ Funciones reutilizables |

---

## 🔧 Resolución de Problemas

### Error: "No se encontró el archivo config.py"
- Asegúrate de que `config.py` esté en el mismo directorio que `woffu_cli.py`

### Error: "Python no está instalado"
- **Windows**: Descargar desde [python.org](https://python.org)
- **Linux**: `sudo apt install python3` (Ubuntu/Debian)
- **macOS**: `brew install python3`

### Error: "No se encontró woffu.py"
- Ejecutar desde el mismo directorio que contiene `woffu.py`

### Error de dependencias
- Ejecutar: `pip install -r requirements.txt`

---

## 💡 Consejos

1. **Siempre usa `--dry-run` primero** para verificar qué se va a ejecutar
2. **Personaliza `config.py`** según tus horarios habituales
3. **El script salta automáticamente** días futuros y fines de semana
4. **La variación aleatoria** hace que los horarios parezcan más naturales
5. **🆕 Usa horarios múltiples** para simular descansos reales (comida, pausas)
6. **🆕 Configura horarios semanales** si tienes diferentes horarios por día
7. **🆕 Valida que no hay solapamientos** - el script detecta automáticamente errores
8. **🆕 Los intervalos múltiples se consolidan** en una sola llamada API para mayor eficiencia

### ⚠️ Consideraciones Importantes

- Los **horarios semanales** omiten días no configurados (útil para trabajo parcial)
- La **variación aleatoria** se aplica a cada intervalo por separado
- Los **intervalos deben estar ordenados** y sin solapamiento
- El **formato de tiempo** puede ser `HH:MM` o `HH:MM:SS` (se normaliza automáticamente)

## Caveats

### Passwords
Be aware, though, this script **STORES YOUR PASSWORD IN PLAIN TEXT IN YOUR COMPUTER**, which is something you should normally never ever
ever do, ever. However, to fully automate the task, I do need the password to send it to the Woffu servers, so I'm afraid there's no way to work around this problem. 

Woffu [does have an API](https://www.woffu.com/wp-content/uploads/2021/07/Woffu_API_Document__Guide_en.pdf) your organization 
can probably use to log you in, or enable so that your user can have an API Key or something. The organization I used to test
this script doesn't so this script is the only way to do it, to my knowledge. If you want to use this script and you want it
to be compatible with your API Key instead of using your password (you should want to!), open an issue and I'll probably do it,
it should be really easy.

