# -*- coding: utf-8 -*-
import os
import telebot
import time
import random
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient
import traceback

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

games={}

#client=MongoClient(os.environ['database'])
#db=client.
#users=db.users 


allfeathers=['-10', '-5', '-5', '3', '1', '1', '0', '3', '7', '6', '2', '8', '?', '3', 'max-', '10', '20', '5', 'max0', '4', 
            '9', '2', '10', '10', 'x2', '4', '2', '1', '5', '15']

@bot.message_handler(commands=['coyote'])
def coyotestart(m):
    if m.chat.id not in games:
        games.update(creategame(m.chat.id, m))
        bot.send_message(m.chat.id, 'Идёт набор в игру! Жми /cjoin для присоединения.')
    else:
        bot.send_message(m.chat.id, 'Игра уже идёт! Жми /cjoin!')


@bot.message_handler(commands=['cjoin'])
def joinn(m):
    if m.chat.id in games:
        if m.from_user.id not in games[m.chat.id]['players']:
            game=games[m.chat.id]
            if len(game['players'])<=len(allfeathers)-5:
                if game['started']==False:
                    try:
                        bot.send_message(m.from_user.id, 'Вы присоединились!')
                        games[m.chat.id]['players'].update(createplayer(m))
                        bot.send_message(m.chat.id, m.from_user.first_name+' присоединился!')
                    except:
                        bot.send_message(m.chat.id, 'Сначала надо написать мне в личку (@Coyotegamebot) хоть что-то!')
            else:
                bot.send_message(m.chat.id, 'Слишком много игроков!')
    else:
        bot.send_message(m.chat.id, 'Нет запущенной игры! /coyote для запуска.')
   

@bot.message_handler(commands=['cstart'])
def startgame(m):
    if m.chat.id in games:
        game=games[m.chat.id]
        if len(game['players'])>1 and game['started']==False:
            game['started']=True
            lst=''
            for ids in game['players']:
                if game['players'][ids]['uname']!=None:
                    lst+='@'+game['players'][ids]['uname']+'\n'
                else:
                    lst+=game['players'][ids]['name']+'\n'
            bot.send_message(game['id'], 'Каждый из игроков получил число! Каждый из вас видит числа остальных, но не видит своего числа!')
            bot.send_message(game['id'], 'Список игроков:\n'+lst)
            t=threading.Thread(target=gostart, args=[game])
            t.start()
            
            
def gostart(game):
    try:
        turnnumbers=[]
        i=1
        while i<=len(game['players']):
            turnnumbers.append(i)
            i+=1
        for ids in game['players']:
            x=random.choice(turnnumbers)
            game['players'][ids]['turnnumber']=x
            turnnumbers.remove(x)
        gamenumbers=allfeathers.copy()
        for ids in game['players']:
            x=random.choice(gamenumbers)
            game['players'][ids]['feather']=x
            gamenumbers.remove(x)
        for ids in game['players']:
            text='Числа игроков:\n\n'
            for idss in game['players']:
                if game['players'][idss]!=game['players'][ids]:
                    text+=game['players'][idss]['name']+': '+game['players'][idss]['feather']+'\n'
            bot.send_message(game['players'][ids]['id'], text)
            
        turn(game)
    except Exception as e:
        bot.send_message(441399484, traceback.format_exc())
    

def turn(game):
    game['currentplayer']+=1
    if game['currentplayer']>len(game['players']):
        game['currentplayer']=1
    for ids in game['players']:
        player=game['players'][ids]
        if player['turnnumber']==game['currentplayer']:
            cplayer=player
    uname=cplayer['uname']
    if uname!=None:
        tx='(@'+cplayer['uname']+')'
    else:
        tx=''
    bot.send_message(game['id'], 'Ход игрока '+cplayer['name']+tx+'!')
    t=threading.Timer(game['turnlen'], nextturn, args=[game])
    t.start()
    game['timer']=t
    

def nextturn(game):
    for ids in game['players']:
        player=game['players'][ids]
        if player['turnnumber']==game['currentplayer']:
            cplayer=player
    if cplayer['ready']==False:
        game['currentnumber']+=1
        game['lastplayer']=cplayer
        bot.send_message(game['id'], 'Игрок '+cplayer['name']+' был АФК и автоматически назвал число на 1 больше: '+str(game['currentnumber'])+'!')
    else:
        bot.send_message(game['id'], cplayer['name']+ ' назвал число: '+str(game['currentnumber'])+'!')
    turn(game)

def createplayer(m):
    return {m.from_user.id:{
        'id':m.from_user.id,
        'name':m.from_user.first_name,
        'uname':m.from_user.username,
        'axes':0,
        'turnnumber':None,
        'feather':None,
        'ready':False
    }
           }

def creategame(id, m):
    return {id:{
        'id':id,
        'currentnumber':0,
        'lastplayer':None,
        'currentplayer':1,
        'players':{},
        'mymessage':m,
        'started':False,
        'timer':None,
        'turnlen':100
    }
           }
    
   
def count(game, m, listt=None):
    player=game['players'][m.from_user.id]
    if player['turnnumber']==game['currentplayer']:
        cplayer=player
    else:
        cplayer=None
    if cplayer!=None:
        if listt==None:
            game['timer'].cancel()
        summ=0
        alls=[]
        if listt==None:
            for ids in game['players']:
                alls.append(game['players'][ids]['feather'])
        else:
            alls=listt
        maxf=-100
        minf=100
        for ids in alls:
            try:
                cnumber=int(ids)
                if cnumber>maxf:
                    maxf=cnumber
                if cnumber<minf:
                    minf=cnumber
            except:
                pass
        if maxf==-100:
            maxf=0
        if minf==100:
            minf=0
        for ids in alls:
            try:
                summ+=int(ids)
            except:
                pass
        for ids in alls:
            if ids=='max-':
                summ-=maxf
                summ-=maxf
            if ids=='max0':
                summ-=maxf
            if ids=='?':
                listt=alls
                listt.remove('?')
                l2=allfeathers.copy()
                for ids in alls:
                    l2.remove(ids)
                new=random.choice(l2)
                listt.append(new)
                count(game, m, listt)
                return 0
        for ids in alls:
            if ids=='x2':
                summ=summ*2
        if game['currentnumber']<=summ:
            winner=game['lastplayer']
            looser=cplayer
        else:
            winner=cplayer
            looser=game['lastplayer']
        pnums=''
        for ids in game['players']:
            pnums+=game['players'][ids]['name']+': '+game['players'][ids]['feather']+'\n'
        bot.send_message(game['id'], 'Ведём подсчёт результатов, создаём интригу...')
        time.sleep(3)
        bot.send_message(game['id'], 'Итоговая сумма: '+str(summ)+'! Числа игроков:\n\n'+pnums)
        bot.send_message(game['id'], 'Победитель: '+winner['name']+'! Проигравший: '+looser['name']+'! Второй получает топор.')
        looser['axes']+=1
        if looser['axes']>=3:
            del game['players'][looser['id']]
            bot.send_message(game['id'], looser['name']+' получил 3й топор и вылетел из игры!')
        lives=''
        for ids in game['players']:
            lives+=game['players'][ids]['name']+': '+str(game['players'][ids]['axes'])+' топор(ов)\n'
        bot.send_message('Оставшиеся игроки:\n\n'+lives)
        if len(game['players'])>1:
            game['currentnumber']=0
            game['lastplayer']=None
            game['currentplayer']=1
            game['timer']=None
            gostart(game)
        else:
            for ids in game['players']:
                last=game['players'][ids]
            bot.send_message(game['id'], 'Последний оставшийся, и он же победитель: '+last['name']+'!')
        


@bot.message_handler(commands=['stop'])
def stopgame(m):
    if m.chat.id in games:
        if m.from_user.id in games[m.chat.id]['players']:
            game=games[m.chat.id]
            if game['lastplayer']!=None:
                count(game, m)
            else:
                bot.send_message(game['id'], 'Вы - первый игрок! Нельзя остановить игру, надо назвать число!')
                    



@bot.message_handler(content_types=['text'])
def texttttt(m):
    if m.chat.id in games:
        if m.from_user.id in games[m.chat.id]['players']:
            game=games[m.chat.id]
            player=game['players'][m.from_user.id]
            if player['turnnumber']==game['currentplayer']:
                cplayer=player
            else:
                cplayer=None
            if cplayer!=None:
                try:
                    number=int(m.text)
                    if number>game['currentnumber']:
                        game['lastplayer']=cplayer
                        game['currentnumber']=number
                        game['timer'].cancel()
                        cplayer['ready']=True
                        nextturn(game)
                    else:
                        bot.send_message(m.chat.id, 'Нужно назвать число больше предыдущего или написать /stop!')
                except:
                    pass
    
    

def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,
                                 parse_mode=parse_mode)   

print('7777')
bot.polling(none_stop=True,timeout=600)

