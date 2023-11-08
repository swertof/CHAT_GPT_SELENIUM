from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import telebot
from telebot import types

import time
from some_links import *
from open_ai_auth import *
from telebot_api import *


options = Options()
myProxy = "138.99.37.58:9372"
proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': myProxy,
    'sslProxy': myProxy,
    'noProxy': ''})
options.proxy = proxy
options.add_argument("--disable-blink-features=AutomationControlled")


url = playground_link
bot = telebot.TeleBot(test_api)
browser = ""

#def timeout_handler(message):
    #browser.close()
    #browser.quit()
    #closing=bot.send_message(message.chat.id,"ИИ закрывается, нажмите Начать для возобновления")
    #bot.register_next_step_handler(closing,initiation)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Начать")
    markup_start.add(btn1)
    bot.send_message(message.chat.id, 
                     "Привет, я нужен для поддержания живого разговора с ИИ!\nНажми кнопку Начать, чтобы запустить программу!\nНажми кнопку Submit, чтобы продолжить генерацию ответа или сгенерировать его заново!\nПосле окончания работы с ИИ нажмите, пожалуйста, кнопку Stop.\nИИ имеет ограничение на количество символов в одной сессии поэтому иногда будет перезапускаться.\nК сожалению время ответа ИИ составляет 15 секунд даже для коротких сообщений, наберитесь терпения",
                     reply_markup=markup_start)
@bot.message_handler(content_types=['text'])
def initiation(message):
    if message.text == "Начать":
        init_message = bot.send_message(message.chat.id,"ИИ запускается...")
        global browser
        browser = webdriver.Chrome(options=options)
        browser.get(url)
        
        #Авторизация
        #time.sleep(3)
        browser.implicitly_wait(10)
        browser.find_element(By.XPATH,'/html/body/div[1]/div[1]/div/div[3]/div/p/button[1]/span/span').click()
        #time.sleep(2)
        browser.implicitly_wait(10)
        browser.find_element(By.ID,'username').send_keys(f"{openai_login}\n")
        time.sleep(2)
        
        browser.find_element(By.ID, 'password').send_keys(f"{openai_pass}\n")
        
        
        #Попадаю в окно ввода информации

        #Клик по окну ввода сообщения
        
        browser.find_element(By.CLASS_NAME, 'text-input-with-focus').click()

        browser.implicitly_wait(10)
        markup_chat=types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1=types.KeyboardButton("Stop")
        btn2=types.KeyboardButton("Submit")
        markup_chat.add(btn1)
        markup_chat.add(btn2)
        done_message=bot.send_message(message.chat.id, "ИИ запущен, начинайте общение!", reply_markup=markup_chat)
        global i
        i = 3
        bot.register_next_step_handler(done_message,chatting)
        
        #Ожидание таймаута



@bot.message_handler(content_types=['text'])
def chatting(message):
    markup_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Начать")
    markup_start.add(btn1)

    markup_chat = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Stop")
    btn2 = types.KeyboardButton("Submit")
    markup_chat.add(btn1)
    markup_chat.add(btn2)
    try:
        if message.text == "Stop":
            browser.close()
            browser.quit()
            closing=bot.send_message(message.chat.id, "ИИ закрывается, нажмите Начать для возобновления", reply_markup=markup_start)
            bot.register_next_step_handler(closing, initiation)
        global i
        if message.text == "Submit":
            #Клик по кнопке Submit
            browser.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[1]/div/div[2]/div/div[2]/div[1]/div/div/div[3]/div[2]/span/button[1]/span/span').click()
            try:
                
                time.sleep(25)
                text_out = browser.find_element(By.XPATH, f'//*[@id="root"]/div[1]/div[1]/div/div[2]/div/div[2]/div[1]/div/div/div[3]/div[1]/div/div/div[{i-1}]/div[2]').text
                response=bot.send_message(message.chat.id, text_out, reply_markup=markup_chat)
                browser.find_element(By.XPATH, f'//*[@id="root"]/div[1]/div[1]/div/div[2]/div/div[2]/div[1]/div/div/div[3]/div[1]/div/div/div[{i}]').click()
                
                i+=2
                bot.register_next_step_handler(response, chatting)
            except Exception as ex:
                print(ex)
                if i==3:
                    response=bot.send_message(message.chat.id, "Да вы же еще ничего не ввели", reply_markup=markup_chat)
                    browser.find_element(By.CLASS_NAME, 'text-input-with-focus').click()
                    bot.register_next_step_handler(response, chatting)
                else:
                    browser.close()
                    browser.quit()
                    closing = bot.send_message(message.chat.id, "ИИ закрывается, нажмите Начать для возобновления", reply_markup=markup_start)
                    bot.register_next_step_handler(closing, initiation)
                    
        else:
            #Запись сообщения в активное окно
            browser.switch_to.active_element.send_keys(message.text)
            
            #Клик по кнопке Submit
            browser.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[1]/div/div[2]/div/div[2]/div[1]/div/div/div[3]/div[2]/span/button[1]/span/span').click()
            
            time.sleep(25)
            # Поиск текста ответа
            text_out = browser.find_element(By.XPATH, f'//*[@id="root"]/div[1]/div[1]/div/div[2]/div/div[2]/div[1]/div/div/div[3]/div[1]/div/div/div[{i-1}]/div[2]').text
            # Клик по кнопке "Добавить сообщение"
            browser.find_element(By.XPATH, f'//*[@id="root"]/div[1]/div[1]/div/div[2]/div/div[2]/div[1]/div/div/div[3]/div[1]/div/div/div[{i}]').click()
            
            i += 2
            response = bot.send_message(message.chat.id, text_out, reply_markup=markup_chat)
            bot.register_next_step_handler(response, chatting)
    except Exception as ex:
        print(ex)
        # browser.close()
        # browser.quit()
        # closing = bot.send_message(message.chat.id, "ИИ закрывается, нажмите Начать для возобновления", reply_markup=markup_start)
        # bot.register_next_step_handler(closing, initiation)

bot.infinity_polling()

#Implicitly wait вместо time.sleep для ускорения. Ждет х секунд до открытия запрашиваемого элемента 