from bs4 import BeautifulSoup
from selenium import webdriver
import time
import telebot


def send_message(message):
    bot = telebot.TeleBot(token='6697261370:AAFTRKjt8yQ_axSHBkqADo5PfZeQfg-0u8k')
    if message == 'Active':
        bot.send_message(428392590, 'ЕСТЬ ГОЛОСОВАНИЯ')
    else:
        bot.send_message(428392590, a)


url = 'https://snapshot.org/#/stgdao.eth'
while True:
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    try:
        a = soup.find('span', class_='bg-green State text-white').text
    except AttributeError:
        a = 'Нет новых голосований'
    send_message(a)
    driver.quit()
    time.sleep(10)

