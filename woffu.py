#!/usr/bin/env python3

import sys
import getopt
import holidays
import requests
import json
import os.path
import getpass
from datetime import date,datetime
from dateutil.tz import tzlocal
from operator import itemgetter

def getDiaryDetails(diary_id, auth_headers, domain):
    """
    (Hypothetical Function)
    Fetches the FULL details for a single diary, including the slots array.
    """
    # ⚠️ This URL is a guess! You must find the correct one in your API documentation.
    url = f"https://{domain}/api/diaries/{diary_id}"
    
    print(f"--- Fetching full details from: {url} ---")
    try:
        response = requests.get(url, headers=auth_headers, timeout=10)
        response.raise_for_status()
        # This should return JSON that contains the 'slots' list with the 'id'
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not get diary details: {e}")
        return None

# Fetch presences
def getPrensence(user_id, auth_headers, domain):
    # Define the date to search
    fromDate = date_to_update
    toDate = date_to_update
    url = f"https://{domain}/api/svc/core/diariesquery/users/{user_id}/diaries/summary/presence?userId={user_id}&fromDate={fromDate}&toDate={toDate}&pageSize=31&includeHourTypes=true&includeNotHourTypes=true&includeDifference=true"
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

def setPresenceFlexible(auth_headers, user_id, diary_id, start_time, end_time, domain):
    """
    Sends a PUT request with a dynamically generated JSON payload.
    Calculates total minutes automatically.
    """
    url = f"https://{domain}/api/diaries/{diary_id}/workday/slots/self"

    # Calculate total minutes from the time strings
    t1 = datetime.strptime(start_time, "%H:%M:%S")
    t2 = datetime.strptime(end_time, "%H:%M:%S")
    total_minutes = int((t2 - t1).total_seconds() / 60)

    # Build the payload dynamically
    payload = {
        "userId": user_id,
        "comments": "",
        "date": date_to_update,
        "slots": [
            {
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
                    "time": start_time,  # <-- Dynamic value
                    "deviceId": None,
                    "signIn": True,
                    "userId": 0  # Note: This specific field seems to be 0 by default
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
                    "time": end_time,  # <-- Dynamic value
                    "deviceId": None,
                    "signIn": False,
                    "userId": 0
                },
                "order": 1,
                "totalMin": total_minutes
            }
        ],
        "diaryId": diary_id
    }
    
    try:
        response = requests.put(url, headers=auth_headers, json=payload)
        response.raise_for_status()
        print(f"Presence modified correctly. Status Code: {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

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
    return requests.post(
        f"https://{domain}/api/svc/signs/signs",
        json = {
            'StartDate': datetime.now().replace(microsecond=0).isoformat()+utc_timezone_hours,
            'EndDate': datetime.now().replace(microsecond=0).isoformat()+utc_timezone_hours,
            'TimezoneOffset': timezone_offset,
            'UserId': user_id
        },
        headers = auth_headers
    ).ok

def saveData(username, password, user_id, company_id, company_country, company_subdivision, domain):
    #Store user/password/id to make less network requests in next logins
    with open(inputfile, "w") as login_info:
        json.dump(
            {
                "username": username,
                "password": password,
                "user_id": user_id,
                "company_id": company_id,
                "company_country": company_country,
                "company_subdivision": company_subdivision,
                "domain": domain
            },
            login_info
        )

print("Woffu Autologin Script\n")
def main(argv):
   global inputfile
   global date_to_update
   global start_time
   global end_time
   start_time = None
   end_time = None
   inputfile = './data.json'
   date_to_update = None
   try:
      opts, args = getopt.getopt(argv,"hi:d:s:e:o:", ["ifile=", "start-time=", "end-time="])
   except getopt.GetoptError:
      print (sys.argv[0] + ' -i <inputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print (sys.argv[0] + ' -i <inputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-d", "--date"):
         date_to_update = arg
      elif opt in ("-s", "--start-time"):
         start_time = arg
      elif opt in ("-e", "--end-time"):
         end_time = arg

   if start_time is None or end_time is None or date_to_update is None:
       print("Error: --date (-d), --start-time (-s) and --end-time (-e) are mandatory.", file=sys.stderr)
       print('Usage: script.py -s <starttime> -e <endtime> -d <date_to_update>', file=sys.stderr)
       sys.exit(2) # Exit with an error code
         
   print(f'Start time: {start_time}')
   print(f'End time: {end_time}')
   print ('Input file is ' + inputfile)
   print ('Date is ' + date_to_update)
   return inputfile
if __name__ == "__main__":
   main(sys.argv[1:])

saved_credentials = os.path.exists(inputfile)
if (saved_credentials):
    with open(inputfile, "r") as json_data:
        login_info = json.load(json_data)
        domain, username, password, user_id, company_id, company_country, company_subdivision = itemgetter(
            "domain",
            "username",
            "password",
            "user_id",
            "company_id",
            "company_country",
            "company_subdivision"
        )(login_info)
else:
    username = input("Enter your Woffu username:\n")
    password = getpass.getpass("Enter your password:\n")

auth_headers = getAuthHeaders(username, password)

if (not saved_credentials):
    domain, user_id, company_id = getDomainUserCompanyId(auth_headers)


if (getHolidays(company_country, company_subdivision)):
    print("Today is a public holiday. What are you doing working?!!. Exiting...")
    exit()

if (signIn(domain, user_id, auth_headers)):
    print ("Login Success!")
    print ("Obtaining Presence...\n")
    presence_data = getPrensence(user_id, auth_headers, domain)
    
    first_diary = presence_data["diaries"][0]
    diary_id_to_update = first_diary["diaryId"]
    #diary_details = getDiaryDetails(diary_id_to_update, auth_headers, domain)
    
    diary_to_update = diary_id_to_update
    start_work_time = start_time
    end_work_time = end_time
    setPresenceFlexible(auth_headers, user_id, diary_to_update, start_work_time, end_work_time, domain)
else:
    print ("Something went wrong when trying to log you in/out.")

if (not saved_credentials):
    saveData(username, password, user_id, company_id, domain)
