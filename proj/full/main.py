# -*- coding: utf-8 -*-
import os
import time

import eel
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


from utils import split_list, captcha_three, CAPTCHA_FILES


eel.init('web')

chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options, executable_path=os.getcwd() + './chromedriver')


def my_send_mail(receiver, attach, subject, email_text, attach_send_delay, captcha_api_key):
        #  жмет "написать"

        driver.find_element_by_xpath("//span[@class='mail-ComposeButton-Text'][contains(.,'Написать')]").click()
        time.sleep(2)
        #  Кому шлем

        driver.find_element_by_xpath("(//div[@is='x-bubbles'])[1]").send_keys(receiver)
        # click random btn for leave field for
        driver.find_element_by_xpath("//button[@data-lego='react'][contains(.,'Копии, От кого')]").click()
        driver.find_element_by_xpath("//button[@data-lego='react'][contains(.,'Копии, От кого')]").click()

        # тема
        driver.find_element_by_xpath("//input[@class='composeTextField ComposeSubject-TextField']").send_keys(subject)

        # текст сообщения
        driver.find_element_by_xpath("//div[contains(@placeholder,'Напишите что-нибудь')]").send_keys(email_text)

        #  Вложения
        if len(attach) >= 1:
            for f in attach:
                driver.find_element_by_class_name("WithUpload-FileInput").send_keys(
                    'C:\\Users\\valinor\Desktop\\projects\\eel_project\\proj\\web\\' + f)
                #  .send_keys(f'/Users/aleksandrmoskalenko/Downloads/mailer/{f}')
                time.sleep(attach_send_delay)

        #  отправить
        driver.find_element_by_xpath("//button[@data-lego='react'][contains(.,'Отправить')]").click()
        time.sleep(3)
        if 'Чтобы отправить его, дождитесь завершения загрузки вложений или удалите их.' in driver.page_source:
            print('Похоже вложения не успели прогрузится, подождем загрузки(15 сек)')
            time.sleep(15)  # даем время на прогрузку
            try:
                #  закрываем окно с инфой о том, что не прогружены вложения
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                driver.find_element_by_xpath("//button[@data-lego='react'][contains(.,'Отправить')]").click()
                time.sleep(4)

            except NoSuchElementException:
                pass

        if 'ComposeReactCaptcha-Captcha' in driver.page_source:
            time.sleep(2)
            while True:
                captcha_solve_data = captcha_three(driver.page_source, captcha_api_key)
                time.sleep(2)
                if captcha_solve_data:

                    # обрабатываем капчу
                    captcha_input = driver.find_element_by_class_name("ComposeReactCaptcha-Input")
                    captcha_input.send_keys(captcha_solve_data)
                    #  жмём отправить
                    driver.find_element_by_xpath("(//button[@data-lego='react'][contains(.,'Отправить')])[2]").click()
                    time.sleep(2)
                    if 'ComposeReactCaptcha-Captcha' in driver.page_source:
                        if ' Возможно, вы отправили слишком много писем сегодня.' in driver.page_source:
                            return True
                        print('Капча не верная, посылаем еще раз...')
                        time.sleep(2)
                        continue
                    else:
                        break
                else:
                    time.sleep(3)
                    continue


        print(f'Отправили:{receiver}')
        time.sleep(3)

def auth_mail(data_list, attach, subject, email_text, default_password_for_email,
                  attach_send_delay, captcha_api_key):
        for email, items in data_list.items():
            print(f'Авторизуемся с аккаунта: {email}')
            driver.get(
                'https://passport.yandex.ru/auth/welcome?from=mail&origin=hostroot_homer_auth_L_ru'
                '&retpath=https%3A%2F%2Fmail.yandex.ru%2F&backpath=https%3A%2F%2Fmail.yandex.ru%3Fnoretpath%3D1')
            time.sleep(5)
            if 'Выберите аккаунт для входа' in driver.page_source:
                driver.find_element_by_class_name('AddAccountButton-wrapper').click()
            driver.find_element_by_class_name('Textinput-Control').send_keys(email)  # поле логина
            driver.find_element_by_class_name('passp-sign-in-button').click()
            time.sleep(5)  # Ждем загрузки ебучего аякса
            src = driver.page_source
            if 'current-password' in src:
                driver.find_element_by_class_name('Textinput-Control').send_keys(default_password_for_email)
                driver.find_element_by_class_name('Button2').click()
                time.sleep(5)
            try:
                driver.find_element_by_xpath(
                    '/html/body/div/div/div[2]/div[2]/div/div/div[2]/div[3]/div/div/form/div[3]/button').click()
                time.sleep(7)
            except NoSuchElementException:
                pass
            if 'Все письма по полочкам' in driver.page_source:
                try:
                    driver.find_element_by_xpath(
                        '//*[@id="nb-1"]/body/div[7]/div/div/div/div/div/div/div/div[2]/div[4]/button[1]').click()
                except NoSuchElementException:
                    try:
                        driver.find_element_by_class_name('mail-Wizard-Close').click()
                    except NoSuchElementException:
                        driver.find_element_by_class_name('mail-Layout-Inner').send_keys(Keys.ESCAPE)
            #driver.get('https://mail.yandex.ru/lite/')
            for item in items:
                if 'Написать' in driver.page_source:
                    my_send_mail(item, attach, subject, email_text, attach_send_delay, captcha_api_key)

        print('Работа завершена')
        time.sleep(10)
        driver.close()


@eel.expose
def main(sender_list, receiver_list, subject, attach_delay, default_password_for_email, api_key, email_text, attachments_files):
    """ Собираем данные с полей """
    data_list = split_list(receiver_list, len(sender_list), sender_list)  # список со вложенными емайлами
    attachment_files = attachments_files  # читаем файлы вложения
    attach_list = list(filter(None, attachment_files))

    subject = str(subject)  # тема сообщений
    email_text = str(email_text)  # текст сообщений
    default_password_for_email = str(default_password_for_email)  # стандартный пароль для аккаунтов-отправителей
    attach_send_delay = int(attach_delay)  # зажержка перед отправление вложений
    captcha = str(api_key)
    # self.close_win()
    auth_mail(data_list, attach_list, subject, email_text, default_password_for_email,
                   attach_send_delay, captcha)
    
    
eel.start('index.html')