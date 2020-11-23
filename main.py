import os
import time
import glob
import base64
from datetime import datetime
from pprint import pprint

import emoji
import schedule
import tweepy
from mojang import MojangAPI

from service import ServiceState
from image_gene import make_image

wait_time = 90

CK = os.environ["ConsumerKey"]
CS = os.environ["ConsumerSecret"]
AT = os.environ["AccessToken"]
AS = os.environ["AccessTokenSecret"]

rebooted = True
service_status_list = {}
waiting_send_list = {}

auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, AS)
api = tweepy.API(auth)

if not os.path.exists("./tmp"):
    os.mkdir("./tmp")

print("api connected")


def get_timestamp():
    timestamp = datetime.today()
    return str(timestamp.strftime("%Y/%m/%d %H:%M"))


def tweet_services_status(status_changed_services: dict):
    global wait_time
    global waiting_send_list

    online_services = []
    unavailable_services = []

    for service in status_changed_services.keys():
        if service in waiting_send_list:
            if waiting_send_list[service].get_elapsed_time().total_seconds() < wait_time:
                print(f"delete from waiting_send_list: {service}")
                del waiting_send_list[service]
        else:
            waiting_send_list[service] = status_changed_services[service]

    for service in waiting_send_list.keys():
        if waiting_send_list[service].get_elapsed_time().total_seconds >= wait_time:
            if waiting_send_list[service].status == "green":
                online_services.append(service)
            elif waiting_send_list[service].status == "red":
                unavailable_services.append(service)

    if len(status_changed_services) > 0:
        print("===detected status of service changed===")
        print("waiting_send_list:")
        pprint(waiting_send_list)
        print("========================================")

    if len(online_services) > 0:
        tweet_online_services(online_services)

    if len(unavailable_services) > 0:
        tweet_unavailable_services(unavailable_services)


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
        "minecraft.net",
        "session.minecraft.net",
        "account.mojang.com",
        "sessionserver.mojang.com",
        "authserver.mojang.com",
        "textures.minecraft.net"
    )
    for service in status.keys():
        if service in show_list:
            if status[service] == "green":
                msg += f"😃{service}\n"
            elif status[service] == "yellow":
                msg += f"😰{service}\n"
            elif status[service] == "red":
                msg += f"💀{service}\n"
    try:
        print("update profile")
        make_image(status)
        api.update_profile_banner(filename="./tmp/tmp.png")
        #api.update_profile(description=msg)
    except Exception as e:
        print(e)
        pprint(msg.rstrip())


def task():
    global service_status_list
    global rebooted
    try:
        status = MojangAPI.get_api_status()
        service_status_change = False
        status_changed_services = {}

        if rebooted:
            update_profile(status)
            rebooted = False
        else:
            status_changed_services = {}
            for service in status.keys():
                if(service_status_list[service] != status[service]):
                    service_status_change = True
                    if(status[service] == "green" or status[service] == "red"):
                        status_changed_services[service] = ServiceState(
                            status=status[service], last_changed_time=datetime.now())

        if service_status_change:
            update_profile(status)

        tweet_services_status(status_changed_services)
        service_status_list = status
    except Exception as e:
        print(e)
        pass


schedule.every(2).seconds.do(task)

while True:
    schedule.run_pending()
    time.sleep(1)
