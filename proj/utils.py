import os
import string
import random


from twocaptcha import TwoCaptcha, SolverExceptions
import requests
from bs4 import BeautifulSoup

CAPTCHA_FILES = []

def split_list(alist, wanted_parts, sender):
    sender_to_dict_keys = {}
    for i in sender:
        sender_to_dict_keys[i] = 0
    print('ss',sender_to_dict_keys)
    length = len(alist)
    q = [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
             for i in range(wanted_parts)]

    for z, v in zip(q, sender_to_dict_keys.keys()):
        sender_to_dict_keys[v] = z
    return sender_to_dict_keys

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def get_captcha_url(html):
    soup = BeautifulSoup(html, "html.parser")
    capcha_block = soup.find('div', {'class': 'b-captcha__info'})
    images = capcha_block.find_all('img')
    for img in images:
        if img.has_attr('src'):
            img_url = img['src']
            return img_url
        else:
            print('captcha not found')


def download_captcha(img_url):
    print(img_url)
    #filename = img_url.split("/")[-1]
    filename = (get_random_string(5)+'.jpg')
    r = requests.get(img_url, timeout=0.5)
    if r.status_code == 200:
        with open(f'{filename}', 'wb') as f:
            f.write(r.content)
    return str(filename)


def captcha_response(img_name, captcha_api_key):
    api_key = os.getenv('APIKEY_2CAPTCHA', f'{captcha_api_key}')
    solver = TwoCaptcha(api_key)
    try:
        result = solver.normal(f'{img_name}')
        return result['code']
    except:
        return False



def captcha_three(html, captcha_api_key):
    img_url = get_captcha_url(html)  # выдергиваем ссылку на изображение
    img_name = download_captcha(img_url)  # качам капчу
    catcha_code = captcha_response(img_name, captcha_api_key)
    return catcha_code
