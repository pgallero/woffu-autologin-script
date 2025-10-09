# Woffu Script

This project provides a set of tools to automate checking in and out of your Woffu organization. It can be used for logging a single day or, more powerfully, for logging an entire month's worth of past working days in a single command.

--

## 🤔 Why?

A new law in my country is forcing people to check in and out of their jobs, every day at the same hours. Sounds to me like a boring, useless chore that could be automated, and what is programming if not automating tasks to make our lives easier.

---

## ⚙️ Setup

You need Python 3.6+ (f-strings rock!), [the requests library](https://pypi.org/project/requests/) and [the holidays library](https://pypi.org/project/holidays/).

`pip install -r requirements.txt`


You've to create and configure a data.json file with the following data:
```json
{
  "username": "<YOUR WOFFU USERNAME>",
  "password": "<YOUR WOFFU PASSWORD>",
  "user_id": <YOUR WOFFU USER ID>,
  "company_id": <YOUR COMPANY ID>,
  "company_country": "<YOUR COMPANY COUNTRY>",
  "company_subdivision": "<YOUR COMPANY SUBDIVISION>",
  "domain": "<YOUR COMPANY WOFFU DOMAIN>",
  "woffu_url": "<YOUR WOFFU URL>"
}

```

If you don't have login data in your data.json you'll be prompted to enter your user and password the first time it starts, and that's it, you don't have to do anything else
but to execute the script whenever you want to log in or out.

## 🚀 Usage


### Manual Usage (Single Day)

To log hours for a specific day, run the `woffu.py` script directly with the date, start time (`-s`), and end time (`-e`).

```bash
python3 woffu.py -d "2025-10-09" -s "08:00:00" -e "15:00:00"
```


### Automated Usage (Full Month)

For true automation, the fichaje_mensual.sh Bash script is the recommended method. It intelligently logs all past working days for a given month, making it perfect for running once to fill out an entire timesheet.


How to use the script:

Save the code above into a file named fichaje_mensual.sh.

Make it executable from your terminal:

```bash
chmod +x fichaje_mensual.sh
```

Configure the YEAR, MONTH, and base start/end times at the top of the script file.

Run it!

```bash
./fichaje_mensual.sh
```

## Caveats

### Passwords
Be aware, though, this script **STORES YOUR PASSWORD IN PLAIN TEXT IN YOUR COMPUTER**, which is something you should normally never ever
ever do, ever. However, to fully automate the task, I do need the password to send it to the Woffu servers, so I'm afraid there's no way to work around this problem. 

Woffu [does have an API](https://www.woffu.com/wp-content/uploads/2021/07/Woffu_API_Document__Guide_en.pdf) your organization 
can probably use to log you in, or enable so that your user can have an API Key or something. The organization I used to test
this script doesn't so this script is the only way to do it, to my knowledge. If you want to use this script and you want it
to be compatible with your API Key instead of using your password (you should want to!), open an issue and I'll probably do it,
it should be really easy.

