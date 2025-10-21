#!/usr/bin/env python3
"""
Woffu Core - Funcionalidad principal de fichaje
Versión simplificada para usar con woffu_unified.py
"""

import sys
import holidays
import requests
import json
import os.path
import getpass
from datetime import date, datetime
from dateutil.tz import tzlocal
from operator import itemgetter
from typing import List, Tuple

def _build_slot(start_time: str, end_time: str, order: int) -> dict:
    """Construye un slot Woffu a partir de horas texto."""
    t1 = datetime.strptime(start_time, "%H:%M:%S")
    t2 = datetime.strptime(end_time, "%H:%M:%S")
    total_minutes = int((t2 - t1).total_seconds() / 60)
    return {
        "id": None,
        "motive": None,
        "in": {
            "new": True,
            "deleted": False,
            "agreementEventId": None,
            "code": None,
            "iP": None,
            "requestId": None,
            "signId": 0,
            "signStatus": 1,
            "signType": 3,
            "time": start_time,
            "deviceId": None,
            "signIn": True,
            "userId": 0
        },
        "out": {
            "new": True,
            "deleted": False,
            "agreementEventId": None,
            "code": None,
            "iP": None,
            "requestId": None,
            "signId": 0,
            "signStatus": 1,
            "signType": 3,
            "time": end_time,
            "deviceId": None,
            "signIn": False,
            "userId": 0
        },
        "order": order,
        "totalMin": total_minutes,
        "deleted": False,
        "new": True
    }

def setPresenceFlexible(auth_headers, user_id, diary_id, start_time, end_time, woffu_url, existing_slots=None):
    """Crea un solo intervalo (retrocompatibilidad)."""
    return setPresenceFlexibleMultiple(auth_headers, user_id, diary_id, [(start_time, end_time)], woffu_url)

def setPresenceFlexibleMultiple(auth_headers, user_id, diary_id, intervals: List[Tuple[str,str]], woffu_url):
    """Envía un PUT con todos los intervalos del día en una sola llamada.

    IMPORTANTE: Esta llamada reemplaza los slots existentes del día en el diario.
    Por eso se utiliza sólo cuando queremos establecer todos los intervalos previstos.
    """
    url = f"https://{woffu_url}/api/diaries/{diary_id}/workday/slots/self"
    # Fecha del día que estamos procesando (variable global establecida en woffu_file_entry* )
    work_date = date_to_update if 'date_to_update' in globals() else datetime.now().strftime("%Y-%m-%d")

    slots = []
    for idx, (s,e) in enumerate(intervals, start=1):
        slots.append(_build_slot(s, e, idx))

    payload = {
        "userId": user_id,
        "comments": "",
        "date": work_date,
        "slots": slots,
        "diaryId": diary_id
    }
    try:
        response = requests.put(url, headers=auth_headers, json=payload)
        response.raise_for_status()
        print(f"✅ Fichajes creados ({len(slots)} intervalo(s)). Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creando fichajes múltiples: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response text: {e.response.text}")
        raise

# aux functions
def getHolidays(company_country, company_subdivision):
    today = date.today().strftime("%Y-%m-%d")
    check_holidays = holidays.CountryHoliday(company_country)
    get_holidays = check_holidays.get(today)
    if (get_holidays):
        print(get_holidays)
        return True
    else:
        return False

def getAuthHeaders(username, password):
    # we need to get the Bearer access token for every request we make to Woffu
    print("Getting access token...\n")
    access_token = requests.post(
        "https://app.woffu.com/token",
        data = f"grant_type=password&username={username}&password={password}"
    ).json()['access_token']
    return {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=utf-8'
    }

def getDomainUserCompanyId(auth_headers):
    # This function should only be called the first time the script runs.
    # We'll store the results for subsequent executions
    print("Getting IDs...\n")
    users = requests.get(
        "https://app.woffu.com/api/users", 
        headers = auth_headers
    ).json()
    company = requests.get(
        f"https://app.woffu.com/api/companies/{users['CompanyId']}", 
        headers = auth_headers
    ).json()
    return company['Domain'], users['UserId'], users['CompanyId']

def signIn(domain, user_id, auth_headers):
    current_time = datetime.now(tzlocal())
    offset_seconds=current_time.utcoffset().total_seconds()
    offset_minutes=offset_seconds/60
    utc_timezone=int(offset_seconds/3600)
    timezone_offset=- + int(offset_minutes)
    utc_timezone_hours='+0{:}'.format(utc_timezone) + ":00"
    #Actually log in
    print("Sending sign request...\n")
    final_url = f"https://{domain}/api/svc/signs/signs"
    return requests.post(
        f"https://{domain}/api/svc/signs/signs",
        json={
            'StartDate': datetime.now().replace(microsecond=0).isoformat() + utc_timezone_hours,
            'EndDate': datetime.now().replace(microsecond=0).isoformat() + utc_timezone_hours,
            'TimezoneOffset': timezone_offset,
            'UserId': user_id
        },
        headers = auth_headers
    ).ok

# Fetch presences
def getPrensence(user_id, auth_headers, woffu_url):
    # Define the date to search
    fromDate = date_to_update
    toDate = date_to_update
    url = f"https://{woffu_url}/api/svc/core/diariesquery/users/{user_id}/diaries/summary/presence?userId={user_id}&fromDate={fromDate}&toDate={toDate}&pageSize=31&includeHourTypes=true&includeNotHourTypes=true&includeDifference=true"
    response = requests.get(url, headers=auth_headers)

    if response.status_code == 200:
        presence_data = response.json()
        for diary in presence_data["diaries"]:
            diary_id = diary["diaryId"]
            user_id = diary["userId"]
            date = diary["date"]
            start_time = diary.get("in", "N/A")
            end_time = diary.get("out", "N/A")
            accepted = diary["accepted"]
            pending = diary["isPending"]
            
            print(f"Diary ID: {diary_id}")
            print(f"User ID: {user_id}")
            print(f"Date: {date}")
            print(f"Start Time: {start_time}")
            print(f"End Time: {end_time}")
            print(f"Accepted: {accepted}")
            print(f"Is Pending: {pending}")
            print("---")
            
        return presence_data
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def saveData(username, password, user_id, company_id, company_country, company_subdivision, domain, woffu_url, data_file='data.json'):
    """Guarda los datos de usuario para futuras ejecuciones"""
    with open(data_file, "w") as login_info:
        json.dump(
            {
                "username": username,
                "password": password,
                "user_id": user_id,
                "company_id": company_id,
                "company_country": company_country,
                "company_subdivision": company_subdivision,
                "domain": domain,
                "woffu_url": woffu_url
            },
            login_info,
            indent=2
        )

def woffu_file_entry(filing_date, start_time, end_time, data_file='data.json'):
    """
    Función principal para realizar un fichaje en Woffu
    
    Args:
        filing_date (str): Fecha en formato YYYY-MM-DD
        start_time (str): Hora de entrada en formato HH:MM:SS
        end_time (str): Hora de salida en formato HH:MM:SS
        data_file (str): Archivo de datos de usuario
    
    Returns:
        bool: True si el fichaje fue exitoso, False en caso contrario
    """
    global date_to_update
    date_to_update = filing_date
    
    try:
        # Cargar credenciales
        with open(data_file, "r") as json_data:
            login_info = json.load(json_data)
            domain, username, password, user_id, company_id, company_country, company_subdivision, woffu_url = itemgetter(
                "domain", "username", "password", "user_id", "company_id",
                "company_country", "company_subdivision", "woffu_url"
            )(login_info)
        
        # Obtener token de autorización
        auth_headers = getAuthHeaders(username, password)
        
        # Verificar si es día festivo
        if getHolidays(company_country, company_subdivision):
            print("⚠️ Hoy es día festivo. ¿Qué haces trabajando?")
            return False
        
        # Realizar login
        if not signIn(domain, user_id, auth_headers):
            print("❌ Error al hacer login en Woffu")
            return False
        
        print("✅ Login exitoso")
        
        # Obtener información de presencia
        presence_data = getPrensence(user_id, auth_headers, woffu_url)
        if not presence_data or not presence_data.get("diaries"):
            print("❌ No se pudo obtener información de presencia")
            return False
        
        # Obtener el diary para el día específico
        first_diary = presence_data["diaries"][0]
        diary_id = first_diary["diaryId"]
        # Crear el fichaje (sin verificar fichajes existentes)
        setPresenceFlexible(auth_headers, user_id, diary_id, start_time, end_time, woffu_url)
        print(f"✅ Fichaje completado para {filing_date}: {start_time} - {end_time}")
        return True
    except Exception as e:
        print(f"❌ Error durante el fichaje: {e}")
        return False
def woffu_file_entry_multi(filing_date: str, intervals: List[Tuple[str,str]], data_file='data.json') -> bool:
    """Fichaje múltiple para un mismo día con varios intervalos.

    Args:
        filing_date: YYYY-MM-DD
        intervals: lista de tuplas (inicio, fin) en formato HH:MM:SS
        data_file: archivo con credenciales
    """
    global date_to_update
    date_to_update = filing_date
    try:
        with open(data_file, "r") as json_data:
            login_info = json.load(json_data)
        domain, username, password, user_id, company_id, company_country, company_subdivision, woffu_url = itemgetter(
            "domain", "username", "password", "user_id", "company_id",
            "company_country", "company_subdivision", "woffu_url"
        )(login_info)

        auth_headers = getAuthHeaders(username, password)

        if getHolidays(company_country, company_subdivision):
            print("⚠️ Hoy es día festivo. ¿Qué haces trabajando?")
            return False

        if not signIn(domain, user_id, auth_headers):
            print("❌ Error al hacer login en Woffu")
            return False

        print("✅ Login exitoso")

        presence_data = getPrensence(user_id, auth_headers, woffu_url)
        if not presence_data or not presence_data.get("diaries"):
            print("❌ No se pudo obtener información de presencia")
            return False

        diary_id = presence_data["diaries"][0]["diaryId"]

        # Ordenar y asegurar no solapamiento (seguridad extra)
        sorted_intervals = sorted(intervals, key=lambda x: x[0])
        for i in range(1, len(sorted_intervals)):
            if sorted_intervals[i-1][1] > sorted_intervals[i][0]:
                raise ValueError(f"Intervalos solapados: {sorted_intervals[i-1]} y {sorted_intervals[i]}")

        setPresenceFlexibleMultiple(auth_headers, user_id, diary_id, sorted_intervals, woffu_url)
        joined = ", ".join([f"{a}-{b}" for a,b in sorted_intervals])
        print(f"✅ Fichajes múltiples completados para {filing_date}: {joined}")
        return True
    except Exception as e:
        print(f"❌ Error durante el fichaje múltiple: {e}")
        return False

def main():
    """Función principal para compatibilidad con llamadas directas"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Woffu Core - Fichaje individual")
    parser.add_argument('-d', '--date', required=True, help='Fecha (YYYY-MM-DD)')
    parser.add_argument('-s', '--start-time', required=True, help='Hora entrada (HH:MM:SS)')
    parser.add_argument('-e', '--end-time', required=True, help='Hora salida (HH:MM:SS)')
    parser.add_argument('-i', '--inputfile', default='data.json', help='Archivo de datos')
    
    args = parser.parse_args()
    
    success = woffu_file_entry(args.date, args.start_time, args.end_time, args.inputfile)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()