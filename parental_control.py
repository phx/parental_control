#!/usr/bin/env python3

import argparse
import configparser
import hashlib
import json
import os
import smtplib
import sys
from datetime import datetime, timezone

# Change to script directory:
script_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_path)

# Set variable values from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
smtp_server = config['smtp']['server']
smtp_port = int(config['smtp']['port'])
smtp_user = config['smtp']['user']
smtp_pass = config['smtp']['pass']
smtp_from_name = config['smtp']['from_name']
smtp_from_addr = config['smtp']['from_addr']
sent_from = f"{smtp_from_name} <{smtp_from_addr}>"
subject = config['smtp']['subject']
recipients = config['alerts']['addresses'].split()
users = config['users']['names'].split()
alert_hosts = config['users']['alert_hosts'].split()
ignored_hosts = config['users']['ignored_hosts'].split()
wordlist = config['files']['wordlist']
log = config['files']['offense_log']

def get_timestamp(time):
	timestamp = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=timezone.utc).astimezone(tz=None)
	timestamp = datetime.strftime(timestamp, '%a %m/%d @ %I:%M:%S %p')
	return timestamp


def get_hash(msg):
	hash = hashlib.sha1(msg.encode('utf-8'))
	hash = hash.hexdigest()
	return hash


def write_hash(msg):
	hash = get_hash(msg)
	msg = msg.replace('\n', ',')
	file = open(log, 'r')
	for line in file:
		if hash in line:
			return False
	with open(log, 'a') as f:
		f.write(f"[{datetime.now().strftime('%Y-%m-%d %I:%M:%S%p')}] [{hash}] - {msg}\n")
	return True


def main(options):
	# Create log if it doesn't exist:
	if not os.path.isfile(log):
		with open(log, 'w'):
			pass
	# Sanity check that users match alert_hosts:
	if not len(users) == len(alert_hosts):
		print('ERROR: Number of users must match number of alert_hosts.')
		sys.exit()
	user_dict = dict(zip(alert_hosts, users))
	# Check for remote config options:
	remote = config['remote_squid_host']['use_remote_squid_host']
	if remote == 'no':
		access_log = config['logs']['squid_access_log']
	else:
		remote_user = config['remote_squid_host']['remote_user']
		remote_host = config['remote_squid_host']['remote_host']
		remote_port = config['remote_squid_host']['remote_port']
		remote_log_path = config['remote_squid_host']['remote_log_path']
	if remote == 'no':
		# Copy local squid access log to current directory:
		try:
			os.popen(f"cp {access_log} .").read()
		except:
			print(f"Couldn't copy {access_log} to current directory.")
			sys.exit()
	else:
		# Check that we have access to remote host:
		whoami = os.popen(f"ssh -p {remote_port} {remote_user}@{remote_host} 'whoami'").read()
		if not whoami.strip() == remote_user:
			print('ERROR: Check that ssh key-based auth is correctly set up between this host and the remote host.')
			sys.exit()
		# Pull remote squid access log from remote_squid_host:
		try:
			print(f"Pulling squid access log from {remote_host}...")
			os.popen(f"scp -P {remote_port} {remote_user}@{remote_host}:{remote_log_path} .").read()
		except:
			print(f"Couldn't pull squid access log from {remote_host}.")
			sys.exit()
	access_log = './access.log'
	lines = open(access_log, 'r')
	with open('./wordlist.txt', 'r') as f:
		words = f.read().split('\n')
	words = [word for word in words if word]
	msgs = []
	for line in lines:
		for word in words:
			if not word in line:
				continue
			entry = json.loads(line)
			url = entry['url']['original']
			if not word in url.lower():
				continue
			referer = entry['http']['request']['referrer']
			timestamp = entry['@timestamp']
			host = entry['host']['hostname']
			if host not in alert_hosts:
				continue
			offender = user_dict[host]
			msg = f'\nUser: {offender}\nKeyword: "{word}"\nTime: {get_timestamp(timestamp)}\nURL: {url}\nReferer: {referer}'
			msgs.append(msg)
	# Get unique list of messages
	msgs = list(set(msgs))
	new_messages = []
	# Print to stdout and send text alerts:
	for msg in msgs:
		if not write_hash(msg):
			continue
		print(msg)
		new_messages.append(msg)
		if options.no_email:
			continue
		email_text = f"From: {sent_from}\nTo: {recipients}\nSubject: {subject}\n\n{msg}"
		try:
			server = smtplib.SMTP_SSL(smtp_server, smtp_port)
			server.ehlo()
			server.login(smtp_user, smtp_pass)
			server.sendmail(sent_from, recipients, email_text)
			server.close()
			print('Alert sent!')
		except:
			print('Error while sending alert.')
	if not new_messages:
		print('\nNothing to alert on.')
	print('\nDone.')

if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('-noemail', default=False, action='store_true', dest='no_email', help='Only show console output - no emails will be sent')
	options = parser.parse_args()
	main(options)
