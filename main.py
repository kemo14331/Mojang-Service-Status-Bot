import os
import time
import datetime
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

auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, AS)
api = tweepy.API(auth)

print("api connected")


def get_timestamp():
    timestamp = datetime.datetime.today()
    return str(timestamp.strftime("%Y/%m/%d %H:%M"))

def tweet_online_services(services: list):
    print("tweet online services.")
    msg = "✅The service has returned to normal.\n"
    if len(services) == 1:
        msg += "Service:\n"
    else:
        msg += "Services:\n"
    for service in services:
        msg += service + '\n'
    msg += "\n" + get_timestamp()
    try:
        api.update_status(status=msg)
    except Exception as e:
        print(e)


def tweet_unavailable_services(services: list):
    print("tweet unavailable services.")
    msg = "❌The service has be currently unavailable.\n"
    if len(services) == 1:
        msg += "Service:\n"
    else:
        msg += "Services:\n"
    for service in services:
        msg += service + '\n'
    msg += "\n" + get_timestamp()
    try:
        api.update_status(status=msg)
    except Exception as e:
        print(e)


def update_profile(status: dict):
    msg = ""
    msg += "Services Status:\n"
    show_list = (
        "session.minecraft.net",
        "account.mojang.com",
        "sessionserver.mojang.com",
        "skins.minecraft.net",
        "authserver.mojang.com",
        "textures.minecraft.net"
    )
    for service in status.keys():
        if service in show_list:
            if status[service] == "green":
                msg += f"🟢{service}\n"
            elif status[service] == "yellow":
                msg += f"🟡{service}\n"
            elif status[service] == "red":
                msg += f"🔴{service}\n"
    try:
        print("update profile")
        api.update_profile(description=msg)
    except Exception as e:
        print(e)
        pprint(msg.rstrip())


def task():
    global service_status_list
    global rebooted
    try:
        status = MojangAPI.get_api_status()
        service_status_change = False
        if rebooted:
            update_profile(status)
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
            if len(back_online_services) > 0:
                tweet_online_services(back_online_services)
            if len(unavailable_services) > 0:
                tweet_unavailable_services(unavailable_services)
        service_status_list = status
    except Exception as e:
        print(e)
        pass


schedule.every(2).seconds.do(task)

while True:
    schedule.run_pending()
    time.sleep(1)
