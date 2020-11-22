import os
import time
from pprint import pprint

import emoji
import schedule
import tweepy
from mojang import MojangAPI

CK = os.environ["ConsumerKey"]
CS = os.environ["ConsumerSecret"]
AT = os.environ["AccessToken"]
AS = os.environ["AccessTokenSecret"]

rebooted = True
service_status_list = {}

profile_header = "This is a bot to tweet when the state of the Mojang services changes."

auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, AS)
api = tweepy.API(auth)


def tweet_online_servies(services: list):
    msg = "[Service Staus Info]\n"
    msg += "✅The service has returned to normal.\n"
    msg += "Services:\n"
    for service in services:
        msg += service + '\n'
    api.update_status(status=msg)


def tweet_unavailable_servies(services: list):
    msg = "[Service Staus Info]\n"
    msg += "❌The service has be currently unavailable.\n"
    msg += "Services:\n"
    for service in services:
        msg += service + '\n'
    api.update_status(status=msg)


def update_profile(status: dict):
    msg = profile_header + '\n'
    msg += "[Service Status]"
    for service in status.keys():
        if service == "green":
            msg += f"🟢{service}: no issues\n"
        elif service == "yellow":
            msg += f"🟡{service}: some issues\n"
        elif service == "red":
            msg += f"🔴{service}: unavailable\n"
    api.update_profile(description=msg)


def task():
    global service_status_list
    status = MojangAPI.get_api_status()
    service_status_change = False
    if rebooted:
        rebooted = False
    else:
        back_online_services = []
        unavailable_services = []
        for service in status.keys():
            if(service_status_list[service] != status[service]):
                service_status_change = True
                if status[service] == "green":
                    back_online_services.append(service)
                elif status[service] == "red":
                    unavailable_services.append(service)
                else:
                    continue
    if service_status_change:
        update_profile(status)
    service_status_list = status


schedule.every(2).second.do(task)

while True:
    schedule.run_pending()
    time.sleep(1)