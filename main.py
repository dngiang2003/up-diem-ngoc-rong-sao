from random import choice, randint
from datetime import datetime
from time import sleep
import requests
import json
import re


IDMIN = 3000
IDMAX = 10000


def getContent():
    """Hàm này trả về 1 lời chúc ngẫu nhiên :)"""
    try:
        with open(r'data/contents.txt', 'r', encoding='utf-8') as r:
            datas = r.read().split("\n")
        r.close()
        return choice(datas)
    except:
        return "Chúc đội ngũ admin NRS một ngày tốt lành ❤️"


def getAccount():
    """Hàm này trả về tài khoản và mật khẩu từ file có định dạng username|password"""
    try:
        with open(r"data/account.txt", "r", encoding="utf-8") as f:
            account = f.read().split("|")
        f.close()
        return account[0], account[1]
    except:
        # tài khoản mật khẩu mặc định nếu lỗi
        return "giangcute", "ahihi123"
   

def getCookie():
    """Hàm này trả về cookie nếu đăng nhập thành công ngược lại trả về None"""
    username, password = getAccount()
    response = requests.post(url="https://ngocrongsao.com/ajax/login",
                        data={
                           "username": username,
                           "password": password,
                           "remember": "on"
                        })
    isCheck = json.loads(response.text)["type"]

    if isCheck == "error":
        return None
   
    cookie = response.cookies.get_dict()["PHPSESSID"]
    return cookie
   

def getIdPost():
    """Hàm này kiểm trả về id của bài viết có thể comment"""
    while True:
        idPost = randint(IDMIN, IDMAX)
        response = requests.get(f"https://ngocrongsao.com/bai-viet/{idPost}").text
        if len(response) > 5000:
            return idPost


def buffComment():
    """Hàm này dùng để buff comment các bài viết theo idPost"""

    global cookie

    idPost = getIdPost()
    content = getContent()

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "vi,en-US;q=0.9,en;q=0.8",
        "content-length": "21",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": f"PHPSESSID={cookie}",
        "origin": "https://ngocrongsao.com",
        "referer": f"https://ngocrongsao.com/bai-viet/{idPost}",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/112.0.0.0",
        "x-requested-with": "XMLHttpRequest"
    }

    payload = {
        "topicId": f"{idPost}",
        "content": content,
    }

    response = requests.post(url="https://ngocrongsao.com/ajax/addcomment",
                        headers=headers,
                        data=payload)
    
    if len(response.text) == 0:
        print(f"Die cookie, tiến hành lấy lại cookie")
        cookie = getCookie()
    else:
        result = json.loads(response.text)
        status = result["type"]
        message = result["message"]

        if status == "error":
            match = re.search(r'\d+', message)
            if match:
                print(f"Vui lòng chờ {match}s")
                sleep(match + 0.5)
            else:
                print("Lỗi không thể comment - chờ 3s")
                sleep(3)
        else:
            now = datetime.now()
            print(f"Thành công ===> {idPost} - {now.strftime('%H:%M:%S-%d/%m/%Y')} - chờ 30s")
            sleep(30.5)

cookie = getCookie()

while True:
    if cookie:
        buffComment()
    else:
        print("Vui lòng kiểm tra lại tài khoản mật khẩu!")
        break
