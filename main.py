import os
import time
from datetime import datetime
from pprint import pprint

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


def get_timestamp():
    timestamp = datetime.utcnow()
    return str(timestamp.strftime("%Y/%m/%d %H:%M")) + "UTC"


def tweet_services_status(status_changed_services: dict):
    global wait_time
    global waiting_send_list

    online_services = []
    unavailable_services = []

    for service in list(status_changed_services.keys()):
        if service in waiting_send_list.keys():
            if waiting_send_list[service].get_elapsed_time().total_seconds() < wait_time:
                print(f"delete from waiting_send_list: {service}")
                del waiting_send_list[service]
        else:
            waiting_send_list[service] = status_changed_services[service]

    for service in list(waiting_send_list.keys()):
        if waiting_send_list[service].get_elapsed_time().total_seconds() >= wait_time:
            if waiting_send_list[service].status == "red":
                unavailable_services.append(service)
            else:
                online_services.append(service)
            del waiting_send_list[service]

    if len(status_changed_services.keys()) > 0:
        print("detected status of service changed.")
        print("waiting_send_list:")
        pprint(waiting_send_list)

    if len(online_services) > 0:
        tweet_services(online_services, ONLINE)

    if len(unavailable_services) > 0:
        tweet_services(unavailable_services, UNAVAILABLE)


def get_services_msg(services: list):
    msg = "Service:\n" if len(services) == 1 else "Services:\n"
    msg.join(list(map(lambda service: service + "\n", services)))
    msg += "\n" + get_timestamp()


ONLINE, UNAVAILABLE = 0, 1
def tweet_services(services: list, mode: int):
    msg = ""
    if mode == ONLINE:
        msg += "✅The service has returned to normal.\n"
    elif mode == UNAVAILABLE:
        msg += "❌The service has be currently unavailable.\n"
    msg += get_services_msg(services)
    try:
        api.update_status(status=msg)
    except Exception as e:
        print(e)


def update_profile(status: dict):
    try:
        print("update profile")
        make_image(status)
        api.update_profile_banner(filename="./tmp/tmp.png")
    except Exception as e:
        print(e)


def is_status_should_notify(status: str, service: str):
    global service_status_list
    if service_status_list[service] == "red":
        return True
    elif status == "red":
        return True
    return False


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
            for service in status.keys():
                if service_status_list[service] != status[service]:
                    service_status_change = True
                    if is_status_should_notify(status[service], service):
                        status_changed_services[service] = ServiceState(
                            status=status[service], last_changed_time=datetime.utcnow())

        if service_status_change:
            update_profile(status)

        tweet_services_status(status_changed_services)
        service_status_list = status
    except Exception as e:
        print(e)
        pass


if __name__ == "__main__":
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)

    if not os.path.exists("./tmp"):
        os.mkdir("./tmp")

    print("api connected")
    schedule.every(2).seconds.do(task)

    while True:
        schedule.run_pending()
        time.sleep(1)
