# certmonitor
Certmonitor is a script to monitor certificates issued for your domain. 

Certmonitor is developed with the lowest common demoninator in mind. Basic output will be printed to stdout. Optionally, basic, plain text email alerting can be set up. Automation and regular monitoring can be set up with a cronjob (details below). 

# Dependencies

Certmonitor relies on external services:

1. sslmate free tier certifiate transparency API.
1. Email account with exteranl SMTP access with a basic username and password.

## sslmate

No API key is required for up to 10 domain queries per hour from an IP address. Details [here](https://sslmate.com/ct_search_api/)

## Email account to send alerts from

I recommend setting up a Gmail account to use for IT infrastructure alerts. Although, given that this script levereges 'smtplib' to send plain text email, any email provider can be used that supports SMTP over SSL with tunneled plain text credentials. 

If you choose to set up a Gmail account to use for alerts, you must open the account, enable MFA, enable SMTP/IMAP, and create an app password. Copy the app passowrd and it will be popualted in to the '.env' file for certmonitor. 

# Installation and Setup

It is recommended to use a Python Virtual Environment (venv) for running certmonitor. Create and activate the venv as outlined below. 

```
python3 -m venv <virtual_environment_name>
source <path_to_venv>/bin/activate
```
Once the Python venv is installed and activated, install Python library dependencies. Pythong library dependencies are provided in a `requirements.txt` file. 
```
python3 -m pip install -r requirements.txt
```

## Setting up the `.env` File

Certmonitor will search for the '.env' file in the same directory as `certmonitor.py`. Below is a template for you to create your own '.env' file:

```
EMAIL_USER = '@gmail.com'
EMAIL_PASSWORD = 'xxxx xxxx xxxx xxxx'
EMAIL_SERVER = 'smtp.gmail.com'
EMAIL_SERVER_PORT = 587
```

## Setting up Log File

Certmonitor will by default use `./certmonitor.log` as the log file for the previously seen certificates. SHA-256 hashes are logged in this file. Each subsequent run will consume this file and compare the currently active certificates found querying sslmate's API to the certificates alerady seen in the log file. If active certificates are seen for the first time, an email alert will be sent if alerting is configured. 

# Usage

```
usage: certmonitor.py [-h] --domain [DOMAIN] [--log [LOG]] [--destemail [DESTEMAIL]]

options:
  -h, --help            show this help message and exit
  --domain [DOMAIN]     Domain or hostname to monitor in CT logs.
  --log [LOG]           Log file for cert hashes to be read from and written to. By default, this is ./certmonitor.log.
                        You must have write permissions to the specified file and enclosing directory. The file and
                        enclosing directory[ies] must already exist.
  --destemail [DESTEMAIL]
                        Email to send alerts to if new certs are found in CT log. If no email provided, result will
                        print to stdout only.
```

## Usage with `cron`

Cron jobs are an easy way to automate regular queries and alerting. Below is an example of a cron job that will run once per hour, at 20 minutes past the hour, utilizing the Python virtual enviornment. 

`20 * * * * /bin/bash -c 'source /home/user/certmonitor/venv/bin/activate && python /home/user/certmonitor/certmonitor.py --domain <domain> --log /home/user/certmonitor/certmonitor.log --destemail <email_recipient> >/dev/null 2>&1'`

You may also use this foundation to create a bash script and call the bash script from the cron job. 

# Results

If a unseen active certificate is found, the output will look as follows, in stdout and in the email alert. 

```
SHA256:  ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
Created: 2024-01-01T00:00:00Z
Host(s): ['*.example.com', 'example.com']
Link: https://crt.sh/?q=ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
```
