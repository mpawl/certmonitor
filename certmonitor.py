#!/usr/bin/python3

import argparse
import requests
import sys
import smtplib
import os
from dotenv import load_dotenv

# Args
parser = argparse.ArgumentParser()
parser.add_argument('--domain', nargs='?', type=str, required=True, help='Domain or hostname to monitor in CT logs.')
parser.add_argument('--log', nargs='?', type=str, default="./certmonitor.log", help='Log file for cert hashes to be read from and written to. By default, this is ./certmonitor.log. You must have write permissions to the specified file and enclosing directory. The file and enclosing directory[ies] must already exist.')
parser.add_argument('--destemail', nargs='?', type=str, help='Email to send alerts to if new certs are found in CT log. If no email provided, result will print to stdout only.')
args = parser.parse_args()

# Set up secrets from .env file
load_dotenv()

# Access the Email settings
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_SERVER = os.getenv('EMAIL_SERVER')
EMAIL_SERVER_PORT = os.getenv('EMAIL_SERVER_PORT')

def send_email(alert_data):
    sent_from = EMAIL_USER
    sent_to = args.destemail
    body = alert_data

    email_text = """\
Subject: CTmon Alert

%s

""" % (str(body))
    try:
        server = smtplib.SMTP(EMAIL_SERVER, EMAIL_SERVER_PORT)
        server.starttls()

        try:
            server.ehlo()
        except:
            print('Could not execute EHLO.')

        try:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
        except: 
            print('Could not log in to email server successfully.')

        server.sendmail(sent_from, sent_to, email_text)
        server.close()

        print('Email sent!')
    except:
        print('Could not conenct to email server or TLS negotiation error.')

def construct_body(alert_set):
    body = ""
    for entry in alert_set:
        alert_entry = "SHA256:  " + str(entry['sha256']) + '\n' + "Created: " + str(entry['not_before']) + '\n' + "Host(s): " + str(entry['dns_names']) + '\n' + "Link: " + str(entry['link']) + '\n\n'
        body += alert_entry

    # Print results to stdout whether or not email alerting configured
    print('\n')
    print(body)

    return body

def do_search(self, f, prev_run_set):
    base_url = f'https://api.certspotter.com/v1/issuances?domain={self}&include_subdomains=true&expand=dns_names&expand=cert'
    alert_list = list()
    try:
        request = requests.get(base_url)
        response = request.json()
        for dct in response:
            if dct['cert_sha256'] not in prev_run_set:
                d = dct['cert']
                alert_list.append({'sha256':d['sha256'], 'dns_names':str(dct['dns_names']), 'not_before':dct['not_before'], 'link':str(f"https://crt.sh/?q={d['sha256']}")})
                f.write(dct['cert_sha256'] + '\n')

    except Exception as e:
        print(e)
    
    return alert_list

def main():
    # Test if we will be sending emails
    send_alert = True
    if any(not var for var in [EMAIL_USER, EMAIL_PASSWORD, EMAIL_SERVER, EMAIL_SERVER_PORT]):
        print(f"Emails will not be sent because email settings are not configured in .env file. To send emails, Please set the EMAIL_ variables in the .env file.")
        send_alert = False

    if not args.destemail:
        print(f"Emails will not be sent because no recipient was specified with '--destemail'.")
        send_alert = False

    # Set up file handler and consume file
    try:
        f = open(args.log, "r+")
    except:
        print(f"Error interacting with log file: {args.log}")

    prev_run_set = set()
    for line in f:
        prev_run_set.add(line.strip())

    alert_list = do_search(args.domain, f, prev_run_set)
    #print(alert_list)
    b = construct_body(alert_list)
    if b and send_alert:
        send_email(b)

if __name__ == "__main__":
    main()
