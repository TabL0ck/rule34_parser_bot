import requests
from bs4 import BeautifulSoup
import os
import telebot
import config
import json
import time

pars = False

bot = telebot.TeleBot(config.token)
@bot.message_handler(commands=['start'])
def start(message):
    global store
    for user in data["users"]:
        if user["id"] == message.from_user.id:
            flag = True
            break
        else:
            flag = False
    if flag == False:
        data["users"].append({"id": message.from_user.id,"bot_id": data["users"][-1]["bot_id"] + 1, "username": message.from_user.username,"blacklist":'',"start_parsing": False,"number_of_page": 0,"tag": "","favourite": '',"fav_status": False,"stop": False,"current_image": 0,"last_image": 0,"now": 0})
        with open('/home/lena/Documents/Parser/user_info.json','w') as file:
            json.dump(data,file, indent=3)
        store.append([])
        
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = telebot.types.KeyboardButton('STOP')
    item2 = telebot.types.KeyboardButton('Blacklist')
    item3 = telebot.types.KeyboardButton('Избранное')
    item4 = telebot.types.KeyboardButton('/help')
    markup.add(item1,item2,item3,item4)
    bot.send_message(message.chat.id,'Well cum {0}'.format(message.from_user.username),reply_markup=markup)
    bot.send_sticker(message.chat.id,open('/home/lena/Documents/Parser/stickers/1.webp','rb'))

@bot.message_handler(commands=['help'])
def helps(message):
    bot.send_message(message.chat.id,'/start - Создает профиль и показывает телеграм клавиатуру.\nЕсли аккаунт уже есть просто показывает клавиатуру.\n\n/abl - Добавляет теги в черный список.\nВводить тэги через пробел.\nПример: /abl furry gay.\n\n/rbl - Убрать тэги из черного списка.\nРаботает аналогично добавлению.\n\n/a - Ответьте на сообщение бота с пикчей этой командой чтобы добавить эту пикчу в избранное.\n\n/r - Ответьте на сообщение бота с пикчей этой командой чтобы удалить эту пикчу из избранного.\n\n/s - Поиск пикчи по ее id.\nВажно: на поиск не работает черный список.\nПример: /s 4383108.\n\n/t - показывает все тэги на пикче.\nПример: /t 4383108')
    bot.send_photo(message.chat.id, open('/home/lena/Documents/Parser/pics/fixik.jpg','rb'),caption = '/report - Если ты нашел баг то можешь сообщить о нем с помощью этой команды. Пример: /report Автор, ты еблан у тебя хэштеги криво вводятся')

@bot.message_handler(commands=['idi_naxuy_prosto_idi_naxuy_sin_sobaki'])
def idi_naxuy_prosto_idi_naxuy_sin_sobaki(message):
    print('start working')
    global pars
    while True:
        for user in data["users"]:
            if user["stop"] == False and user["start_parsing"] == True and user["current_image"] <= user["last_image"]:
                pars = True
              #  print(user["current_image"],user["last_image"],user["now"],user["start_parsing"],user["number_of_page"],user["tag"],user['stop'])
                if user["current_image"] % 42 == 0:
                    store[user["bot_id"] - 1].clear()
                    user["now"] = 0
                    url = 'https://rule34.xxx/index.php?page=post&s=list&tags='+user["tag"]+'&pid='+str(user["current_image"])
                    soup = BeautifulSoup(requests.get(url).text,'html.parser')
                    img = soup.find_all('span', {'class':'thumb'})
                    for item in img:
                        store[user["bot_id"] - 1].append(item)
                try:
                    id = store[user["bot_id"] - 1][user["now"]].find('a').get('id').strip('p')
                except:
                    bot.send_message(user["id"],'Пикчи по тегу {0} скамчались'.format(user["tag"]))
                    user["current_image"] = 0
                    user["last_image"] = 0
                    user["now"] = 0
                    user["start_parsing"] = False
                    user["number_of_page"] = 1
                    user["tag"] = ""
                    store[user["bot_id"] - 1].clear()
                    user['fav_status'] = False
                    break
                url = 'https://rule34.xxx/index.php?page=post&s=view&id={0}'.format(id)
                soup = BeautifulSoup(requests.get(url).text,'html.parser')
                try:
                    skip = False
                    link = soup.find('img',{'id':'image'}).get('src')
                    pics_tags = soup.find('img',{'id':'image'}).get('alt')
                    tags_list = pics_tags.split()
                    bl_temp = user["blacklist"].split()
                    for items in tags_list:
                        if items.replace(' ','').lower() in bl_temp:
                            skip = True
                    if skip == False:
                        if link[-len(str(id))-4] == 'g':
                            bot.send_video(user["id"],link,caption=id)
                        else:
                            bot.send_photo(user["id"],link,caption=id)
                    else:
                        bot.send_message(user["id"],'{0} имеет тэг из черного списка'.format(id))
                        skip = False
                except:
                    try:
                        skip = False
                        link = soup.find('source',{'type':'video/mp4'}).get('src')
                        video_tags = soup.find('meta',{'name':'keywords'}).get('content')
                        tags_list = video_tags.split()
                        bl_temp = user["blacklist"].split()
                        for items in tags_list:
                            if items.replace(',','').lower() in bl_temp:
                                skip = True
                        if skip == False:
                            bot.send_video(user["id"],link,caption=id)
                        else:
                            bot.send_message(user["id"],'{0} имеет тэг из черного списка'.format(id))
                            skip = False
                    except Exception as error:
                        print('{0} in parsing: {1}'.format(user["username"],error))
                        bot.send_message(user["id"],'Не могу отправить {0}, слишком большое видео'.format(id))
                user["current_image"] += 1
                user["now"] += 1
            elif user["fav_status"] == True and user["current_image"] < user["now"] and user["stop"] == False:
                pars = True
                if user["current_image"] == 0:
                    temp = user["favourite"].split()
                    user["now"] = len(temp)
                    for item in temp:
                        store[user["bot_id"] - 1].append(item)
                id = store[user["bot_id"] - 1][user["current_image"]]
                url = 'https://rule34.xxx/index.php?page=post&s=view&id={0}'.format(id)
                soup = BeautifulSoup(requests.get(url).text,'html.parser')
                try:
                    link = soup.find('img',{'id':'image'}).get('src')
                    if link[-len(str(id))-4] == 'g':
                        bot.send_video(user["id"],link,caption=id)
                    else:
                        bot.send_photo(user["id"],link,caption=id)
                except:
                    try:
                        link = soup.find('source',{'type':'video/mp4'}).get('src')
                        bot.send_video(user["id"],link,caption=id)
                    except Exception as error:
                        print('{0} in parsing: {1}'.format(user["username"],error))
                        bot.send_message(user["id"],'Не могу отправить {0}, слишком большое видео'.format(id))
                user["current_image"] += 1
                if user["current_image"] == user["now"]:
                    bot.send_message(user["id"],'Избранное пользователя {0}'.format(user["username"]))
                    user["current_image"] = 0
                    user["last_image"] = 0
                    user["now"] = 0
                    user["start_parsing"] = False
                    user["number_of_page"] = 1
                    user["tag"] = ""
                    store[user["bot_id"] - 1].clear()
                    user['stop'] = False
                    user['fav_status'] = False
                
            elif user["stop"] == True:
                user["current_image"] = 0
                user["last_image"] = 0
                user["now"] = 0
                user["start_parsing"] = False
                user["number_of_page"] = 1
                user["tag"] = ""
                store[user["bot_id"] - 1].clear()
                user['stop'] = False
                user['fav_status'] = False
        if pars == False:
            time.sleep(5)
            pars = True
@bot.message_handler(commands=['abl'])
def add_to_blacklist(message):
    for user in data["users"]:
        if user["id"] == message.from_user.id:
            for item in message.text.replace('/abl','').split():
                user["blacklist"]+= '{0} '.format(item)
            with open('/home/lena/Documents/Parser/user_info.json','w') as file:
                json.dump(data,file, indent=3)
            bot.send_message(message.chat.id,'Черный список успешно обновлен')
            break

@bot.message_handler(commands=['rbl'])            
def remove_from_blacklist(message):
    for user in data["users"]:
        if user["id"] == message.from_user.id:
            try:
                for item in message.text.replace('/rbl','').split():
                    user["blacklist"] = user["blacklist"].replace('{0} '.format(item), '')
                with open('/home/lena/Documents/Parser/user_info.json','w') as file:
                    json.dump(data,file, indent=3)
                bot.send_message(message.chat.id,'Черный список успешно обновлен')
            except Exception as error:
                print('{0} in remove_from_blacklist: {1}'.format(user["username"],error))
                bot.send_message(message.chat.id,'something going wrong')
            break

@bot.message_handler(commands=['a'])
def add_to_favourite(message):
    for user in data["users"]:
        if user["id"] == message.from_user.id:
            try:
                int(message.reply_to_message.caption)
                user["favourite"] += '{0} '.format(message.reply_to_message.caption)
                bot.send_message(message.chat.id,'{0} добавлено в избранное'.format(message.reply_to_message.caption))
                with open('/home/lena/Documents/Parser/user_info.json','w') as file:
                    json.dump(data,file, indent=3)
            except:
                try:
                    for item in message.text.replace('/a','').split():
                        int(item)
                        user["favourite"] += '{0} '.format(item)
                    with open('/home/lena/Documents/Parser/user_info.json','w') as file:
                        json.dump(data,file, indent=3)
                    bot.send_message(message.chat.id,'Все элементы добавлены в избранное')
                except Exception as error:
                    print('{0} in add_to_favourite: {1}'.format(user["username"],error))
            break

@bot.message_handler(commands=['r'])
def remove_from_favourite(message):
    for user in data["users"]:
        if user["id"] == message.from_user.id:
            try:
                int(message.reply_to_message.caption)
                user["favourite"] = user["favourite"].replace('{0} '.format(message.reply_to_message.caption), '')
                bot.send_message(message.chat.id,'{0} удалено из избранного'.format(message.reply_to_message.caption))
                with open('/home/lena/Documents/Parser/user_info.json','w') as file:
                    json.dump(data,file, indent=3)
            except:
                try:
                    for item in message.text.replace('/r','').split():
                        int(item)
                        user["favourite"] = user["favourite"].replace('{0} '.format(item), '')
                    bot.send_message(message.chat.id,'Все элементы удалены из избранного')
                    with open('/home/lena/Documents/Parser/user_info.json','w') as file:
                        json.dump(data,file, indent=3)
                except Exception as error:
                    print('{0} in remove_from_favourite: {1}'.format(user["username"],error))
            break

@bot.message_handler(commands=['s'])
def search(message):
    id = message.text.replace('/s','')
    try:
        url = 'https://rule34.xxx/index.php?page=post&s=view&id={0}'.format(id)
        soup = BeautifulSoup(requests.get(url).text,'html.parser')
        link = soup.find('img',{'id':'image'}).get('src')
        if link[-len(str(id))-3] == 'g':
            bot.send_video(message.chat.id,link,caption=id)
        else:
            bot.send_photo(message.chat.id,link,caption=id)
    except:
        try:
            link = soup.find('source',{'type':'video/mp4'}).get('src')
            bot.send_video(message.chat.id,link,caption=id)
        except Exception as error:
            print('{0} in search: {1}'.format(message.from_user.username,error))
        
@bot.message_handler(commands=['t'])
def tags(message):
    id = message.text.replace('/t','')
    try:
        url = 'https://rule34.xxx/index.php?page=post&s=view&id={0}'.format(id)
        soup = BeautifulSoup(requests.get(url).text,'html.parser')
        pics_tags = soup.find('img',{'id':'image'}).get('alt').replace(' ','     ')
        bot.send_message(message.chat.id,pics_tags.replace(',',''))
    except:
        try:
            video_tags = soup.find('meta',{'name':'keywords'}).get('content').replace(' ','     ')
            bot.send_message(message.chat.id,video_tags)
        except Exception as error:
            print('{0} in tags: {1}'.format(message.from_user.username,error))
        
@bot.message_handler(commands=['report'])
def report(message):
    bot.send_message(439316103,'{0}: {1}'.format(message.from_user.id,message.text.replace('/report','')))
    bot.send_message(message.chat.id,'Репорт отправлен')

@bot.message_handler(commands=['update_info'])
def update_info(message):
    if message.from_user.id == 439316103:
        for user in data["users"]:
            bot.send_message(user["id"],'Теперь бот умеет кидать гифки и видосы до 20 Мб')
            bot.send_sticker(user["id"],open('/home/lena/Documents/Parser/stickers/update.webp','rb'))
            
@bot.message_handler(content_types=['text'])
def parsing_bot(message):
    for user in data["users"]:
        if user["id"] == message.from_user.id:
            if message.chat.type == 'private':
                if message.text == 'Blacklist':
                    def show_blacklist():
                        temp = user["blacklist"].replace(' ','      ')
                        bot.send_message(message.chat.id,temp)
                    show_blacklist()
                elif message.text == 'test':
                    pass
                elif message.text == 'Избранное':
                    user["now"] = 1
                    user["fav_status"] = True
                elif message.text == 'STOP':
                    user["stop"] = True
                else:
                    user["tag"] = message.text.lower().replace(' ','_')
                    def searching():
                        def page_count():
                            try:
                                url = 'https://rule34.xxx/index.php?page=post&s=list&tags='+user["tag"]+'&pid='+'0'
                                soup = BeautifulSoup(requests.get(url).text,'html.parser')
                                last_page = int(soup.find('a',{'alt':'last page'}).get('href').strip('?page=post&s=list&tags=',).strip(user["tag"]).strip('&pid='))
                                total_page = last_page/42
                                return total_page + 1
                            except:
                                return 1
                        bot.send_message(message.chat.id,'Всего страниц = {0}\nВажно: Если страница 1 она может быть пуста!'.format(page_count()))
                        user["number_of_page"] = page_count()
                        user["start_parsing"] = True
                        user["last_image"] = user["number_of_page"] * 42 -1
                    searching()
            break

        
    
with open('/home/lena/Documents/Parser/user_info.json','r') as file:
    data = json.load(file)

store = []
for i in range(data["users"][-1]["bot_id"]):
    store.append([])

def reset():
    for user in data["users"]:
        user["current_image"] = 0
        user["last_image"] = 0
        user["now"] = 0
        user["start_parsing"] = False
        user["number_of_page"] = 1
        user["tag"] = ""
        user['stop'] = False
        user['fav_status'] = False
reset()
bot.polling(none_stop=True)


'''
                    except:
                        try:
                            skip = False
                            link = soup.find('source',{'type':'video/mp4'}).get('src')
                            print(link)
                            video_tags = soup.find('meta',{'name':'keywords'}).get('content')
                            tags_list = video_tags.split()
                            for items in tags_list:
                                if items.replace(' ','').lower() in user["blacklist"]:
                                    skip = True
                            if skip == False:
                                p = requests.get(link)
                                out = open('Documents/Parser/outputs/'+str(id)+'.mp4', 'wb')
                                out.write(p.content)
                                out.close()
                                bot.send_video(user["id"],open('/home/lena/Documents/Parser/outputs/{0}.mp4'.format(id),'rb'),caption=id)
                            else:
                                bot.send_message(user["id"],'{0} имеет тэг из черного списка'.format(id))
                                skip = False
'''
