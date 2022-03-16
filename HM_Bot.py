import os
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import bs4
import requests
from datetime import datetime


token = "c7974328168f8d8d0a46d707d25f175c314e3a46dea31708aa2452845b8037d9f4735ccd2cb98623ce65a"
vk_group_id = 210986020
vk_session = vk_api.VkApi(token=token)
vk_session.get_api()
longpool = VkBotLongPoll(vk_session, vk_group_id)
adm = [708270480, 586097800, 558905265]
commands = ["привет", "дз", "123", "расписание", "очистка"]
timetable = {
    "русский язык": [1, 4],
    "алгебра": [2, 3, 4],
    "физика": [2, 5],
    "химия": [1, 4],
    "английский язык": [1, 3, 5],
    "геометрия": [1, 5],
    "история": [1, 5],
    "биология": [1, 5],
    "литература": [2, 5],
    "обж": [2],
    "информатика": [2],
    "география": [2, 3],
    "технология отраслей": [3],
    "культурология": [3],
    "проектная деятельность": [3],
    "музыка": [3],
    "технология": [4],
}


def get_name(user):
    request = requests.get("https://vk.com/id" + str(user))
    bs = bs4.BeautifulSoup(request.text, "html.parser")
    user_name = clean_all_tag_from_str(bs.findAll("title")[0])
    return user_name.split()[0]


def get_time():
    request = requests.get("https://my-calend.ru")
    bs = bs4.BeautifulSoup(request.text, "html.parser")
    time = clean_all_tag_from_str(str(bs.findAll("p"))).split()[3]
    result = ""
    for c in time:
        if c.isdigit():
            result += str(c)
    return int(result)


def clean_all_tag_from_str(string_line):
    result = ""
    flag = True
    for i in list(string_line):
        if flag:
            if i == "<":
                flag = False
            else:
                result += i
        else:
            if i == ">":
                result += " "
                flag = True
    return result


def send_msg(user, message):
    vk_session.method('messages.send', {'user_id': user, 'message': str(message), 'random_id': 0})


def wait(user):
    for event in longpool.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and user == event.object.message['from_id']:
            return event


def admin(user):
    send_msg(user, "Введите название предмета")
    subject = wait(user).object.message['text'].lower()
    if subject in timetable:
        week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        today = datetime.now().strftime("%A")
        temp = week.index(today)
        day = 0
        counter = 0
        for i in range(temp + 1, temp + 8):
            counter += 1
            if i % 7 in timetable[subject]:
                day = get_time() + counter
                break
        arg = ""
        if os.path.isfile(f"days/{day}.txt"):
            arg = "a"
        else:
            arg = "w"
        with open(f"days/{day}.txt", arg) as f:
            send_msg(user, "Введите домашние задание")
            f.write(f"{subject}: {str(wait(user).object.message['text'])}\n")
    else:
        send_msg(user, "Предмет введен неверно")
        admin(user)


def read_files(file):
    result = ""
    with open(file + ".txt", "r") as f:
        for line in f.readlines():
            result += line + "\n"
    return result


def new_message(message, user):
    if message.lower() == commands[0]:
        return f"Привет, {get_name(user)}!"
    elif message.lower() == commands[1]:
        if os.path.isfile(f"days/{str(get_time() + 1)}.txt"):
            return read_files(f"days/{str(get_time() + 1)}")
        else:
            return "Ничего не задано"
    elif message.lower() == commands[2]:
        if user in adm:
            admin(user)
            return "Подтвержденно"
        else:
            with open(user_id, "a") as f:
                f.write(str(user_id))
            return "Ожидайте подтверждения"
    elif message.lower() == commands[3]:
        return read_files("TT")
    elif message.lower() == commands[4]:
        files = os.listdir("days")
        today = get_time()
        for c in files:
            if int(c[:-4]) < today:
                os.remove("days/" + c)
        return "Очистка завершена"
    else:
        return "???"


print("Server started")
while True:
    try:
        for event in longpool.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                request = event.object.message['text']
                user_id = event.object.message['from_id']
                print("New message:")
                print(f"For me by: {user_id}")
                send_msg(user_id, new_message(request, user_id))
                print("Text: ", request)
    except Exception as e:
        print(e)
