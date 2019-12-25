#!/usr/bin/env python3
from os import environ
from multiprocessing import Process
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser
from telethon.tl.functions.messages import SendMessageRequest
from alchemysession import AlchemySessionContainer

import telethon.sync
import logging
import configparser
import datetime
import time
import random
import sys
import pika
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)
logger = logging.getLogger(__name__)


#Set up session and connect to Tg
proxy_chan_id = 1151984662

container = AlchemySessionContainer(environ['DATABASE_URL'])
session_name = environ.get('TG_SESSION', 'session')
session = container.new_session(session_name)

user_phone = environ['TG_PHONE']
client = TelegramClient(
    session, int(environ['TG_API_ID']), environ['TG_API_HASH'],
    proxy=None
)

def code_cb():
    return environ['TG_CODE']

client.start(phone=user_phone, code_callback=code_cb)


targetChat = 'chtwrsbot'

#Initialize OfferTracker
class OfferTracker:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.credentials = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(host='api.chatwars.me',
                                       port=5673,
                                       virtual_host='/',
                                       credentials=self.credentials,
                                       ssl=True,
                                       socket_timeout=10)
        self.auth = {
                    "token": token,
                    "action": "requestProfile"
                    #"payload": {  
                        #"requestId": uuid, #requestId of parent authAdditionalOperation 
                        #"authCode": code #code supplied by user for this requestId  
       }  

        
        
        self.options = [self.auth, "token", "offertracker", "requestProfile"]
    def establish_connection(self):
        self.connection = pika.BlockingConnection(self.parameters)
        print ("Connected")
        #self.connection.close()
        #print ("Disconnected")

    def create_channel(self):
        self.channel = self.connection.channel()
        print ("Channel created")

    def begin_consume(self):
        self.channel.basic_consume(self.check_profile,
                      queue=self.username+"_i")
        print ("Begin consuming...")
        startTime = time.time()

        while self.channel._consumer_infos:
            self.channel.connection.process_data_events(time_limit=1)
            currentTime = time.time()
            if (currentTime - startTime) > 480.0:        
                self.close_channel()
                
    def publish(self, message):
        self.convert_Body_to_Json(message)
        self.channel.basic_publish(self.username+'_ex',
        self.username+'_o',
        message,
        pika.BasicProperties(content_type='text/plain',
                            delivery_mode=1))
                
    def close_channel(self):
        print ("Closing Channel")
        self.channel.stop_consuming()
        self.channel.close()
        print ("Channel Closed")
        
    def convert_Json_to_Body(self, JsonString):
        #JsonString = JsonString.decode("utf-8")
        body = json.loads(JsonString)
        return body

    def convert_Body_to_Json(self, body):
        self.JsonString = json.dumps(body)
        return self.JsonString
    
    def check_profile(self, channel, method_frame, header_frame, body):
        #print (body)
        try:
            newProfile = self.convert_Json_to_Body(body)
            print (newProfile)
            
        #except KeyError:
            #pass
        except UnicodeEncodeError:
            del newProfile["payload"]["profile"]["castle"]
            print (newProfile["payload"])
            return newProfile
        self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    
    def sort_info(self, channel, method_frame, header_frame, body):
        #print (method_frame.delivery_tag)
        #print (body)
        self.offerdict = self.convertJson(body)
        self.item = self.offerdict["item"]
        self.price = self.offerdict["price"]
        self.buy_item(self.item, self.price)
        self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        self.startProcessTime = time.process_time()
        #print (offerdict)
        self.seller = self.offerdict["sellerName"]
        #try:
            #print (self.item)
            #print (self.price)
        #except UnicodeEncodeError:
            ##startProcessTime = time.process_time()
            #self.item = self.item[1:]
            ##endProcessTime = time.process_time()
            ##print (endProcessTime-startProcessTime)
            #print (self.item)
            #print (self.price)
            ##requests.get(website+"/sendmessage?chat_id="+str(chatid)+"&text= Item: "+ item + ", Seller: " + seller + ", price: "+str(price))
        #self.check_item(self.item)
    
    def check_item(self, item):
        if item == "Bottle of Rage" or item == "Bottle of Peace":
            #print (self.seller + " is selling: "+self.item+ " (" + str(self.price) + ")")
            return True
        if item == "Bottle of Greed":
            self.buy_item(self.item, self.price)
        
    def buy_item(self, item, price):
        if price <= 20:
            if item == "Bottle of Greed":
                client.send_message(targetChat, '/wtb_p09_1')
                self.endProcessTime = time.process_time()
                print ("HA! SNIPED!" + str(self.endProcessTime-self.startProcessTime))
            elif item == "Bottle of Peace":
                client.send_message(targetChat, '/wtb_p06_1')
    def start(self):
        self.establish_connection()
        self.create_channel()

    def getProfile(self):
        self.publish(self.options[1])
        self.begin_consume()

username = environ.get('OFFERTRACKER_USERNAME')
password = environ.get('OFFERTRACKER_PASSWORD')
token = environ.get('TOKEN')
trackOffers = OfferTracker(username, password)
#trackOffers.start()
                
#startOfferTracker()

#Set up Autobot
def stopForay():
    time.sleep(random.randint(1,10))
    print ("Stopping foray")
    client.send_message(targetChat, '/go')
    time.sleep(20)
    setDef()
    
def setDef():
    time.sleep(random.randint(1,10))
    #print ("Time to defend")
    client.send_message(targetChat, '\U0001F6E1'+'Defend')
    print ("Setting defence")

def checkTime():
    currentTime = datetime.datetime.now()
    return currentTime

def letsGoForest():
    time.sleep(random.randint(1,10))
    print ("Going to the forest")
    client.send_message(targetChat, '\U0001F332'+'Forest')
    
def goArena():
    time.sleep(random.randint(1,10))
    print ("Going to the Arena")
    client.send_message(targetChat, '▶️Fast fight')
    
def equipArenaWeapons():
    time.sleep(random.randint(1,10))
    print ("Equipping Arena weapons")
    client.send_message(targetChat, '/on_w28')
    time.sleep(random.randint(1,10))
    client.send_message(targetChat, '/on_u101')

def equipDefWeapons():
    time.sleep(random.randint(1,10))
    print ("Equipping Defend weapons")
    client.send_message(targetChat, '/on_w31')
    time.sleep(random.randint(1,10))
    client.send_message(targetChat, '/on_506')

def brewExp():
    time.sleep(random.randint(1,10))
    print ("Brewing")
    client.send_message(targetChat, '/craft_23')
    time.sleep(random.randint(1,5))
    client.send_message(targetChat, '/brew_507')
    time.sleep(random.randint(1,5))
    client.send_message(targetChat, '/use_507')

def engageMonsters(endTime engageOffset):
    time.sleep(random.randint(1, 10))
    print ("Engaging monster")
    client.send_message(targetChat, '/engage')
    time.sleep(25)
    engageEndTime = checkTime()
    if engageEndTime.minute - endTime.minute >= 1:
        engageOffset += 1
    
def startAutobot():
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    #print(messages)
    #print(str(messages[0].from_id) + ":")
    #start = True
    #startProcessTime = 0
    #endProcessTime = 0
    #sleepTime = 0
    currentTime = checkTime()
    startTime = 0
    timeOffset = 0
    engageOffset = 0
    while True: #start == True:
        endTime = checkTime()
        if startTime != 0:
            if endTime.second - startTime >= 1:
                timeOffset = 1
            else:
                timeOffset = 0
        startTime = endTime.second
        #tinyProcessTime = startProcessTime - endProcessTime# - sleepTime
        #print ("start: "+str(startProcessTime)+", end: "+str(endProcessTime)
        messages = client.get_messages(targetChat, limit=5)
        #newMessage = "     "+str(messages[0].message)
        #print(str(messages[0].from_id) + ":")
        #print(newMessage.translate(non_bmp_map))
        
        #processTime = 0
        print (str(endTime.hour) +" : " + str(endTime.minute) + " : " + str(endTime.second) +"."+str(endTime.microsecond))#(currentTime)

        #set defence
        if endTime.hour == 22 and endTime.minute == 58:
            setDef()
            #start = False
        elif endTime.hour == 6 and endTime.minute == 58:
            setDef()
            #start = False
        elif endTime.hour == 14 and endTime.minute == 58:
            setDef()
            #start = False

        #catch forays         
        if messages[0].find('/go') != -1:
            #print (messages[0].message)
            #print (str(endTime)+" - Foray identified")
            stopForay()

        if messages[0].message.find('/engage') != -1:
            engageMonsters(endTime, engageOffset)
                
        #morning forest
        if endTime.hour == 23 and endTime.minute == 5:
            letsGoForest()            
        elif endTime.hour == 23 and endTime.minute == 11:
            letsGoForest()            
        elif endTime.hour == 23 and endTime.minute == 17:
            letsGoForest()               
        elif endTime.hour == 23 and endTime.minute == 23:
            letsGoForest()
        elif endTime.hour == 23 and endTime.minute == 29:
            letsGoForest()
        elif endTime.hour == 23 and endTime.minute == 35:
            letsGoForest()
        elif endTime.hour == 23 and endTime.minute == 41:
            letsGoForest()
        elif endTime.hour == 23 and endTime.minute == 47:
            letsGoForest()
        elif endTime.hour == 23 and endTime.minute == 53:
            letsGoForest()
        elif endTime.hour == 23 and endTime.minute == 59:
            letsGoForest()
        elif endTime.hour == 24 and endTime.minute == 5:
            letsGoForest()
        elif endTime.hour == 24 and endTime.minute == 11:
            letsGoForest()

        #night forest
        if endTime.hour == 21 and endTime.minute == 5:
            letsGoForest()
        elif endTime.hour == 21 and endTime.minute == 13+engageOffset:
            letsGoForest()            
        elif endTime.hour == 21 and endTime.minute == 21+engageOffset:
            letsGoForest()               
        elif endTime.hour == 21 and endTime.minute == 29+engageOffset:
            letsGoForest()
        elif endTime.hour == 21 and endTime.minute == 37+engageOffset:
            letsGoForest()
        elif endTime.hour == 21 and endTime.minute == 45+engageOffset:
            letsGoForest()
            engageOffset = 0
            
        elif endTime.hour == 13 and endTime.minute == 5:
            letsGoForest()
        elif endTime.hour == 13 and endTime.minute == 13+engageOffset:
            letsGoForest()            
        elif endTime.hour == 13 and endTime.minute == 21+engageOffset:
            letsGoForest()               
        elif endTime.hour == 13 and endTime.minute == 29+engageOffset:
            letsGoForest()
        elif endTime.hour == 13 and endTime.minute == 37+engageOffset:
            letsGoForest()
        elif endTime.hour == 13 and endTime.minute == 45+engageOffset:
            letsGoForest()

        #equip weapons to go to arena
        if endTime.hour == 8 and endTime.minute == 28:
            equipArenaWeapons()

        #arena
        if messages[0].message.find('stronger than') != -1 or (endTime.hour == 8 and endTime.minute == 45) or messages[0].message.find('find an opponent') != -1:
            goArena()

        #equip normal def weapons after arena
        if messages[0].message.find('heal your wounds') != -1:
            equipDefWeapons()
            #brew exp
            brewExp()
            
        #processTime = endProcessTime - startProcessTime
        #sleepTime = 60-processTime-tinyProcessTime
        
        #print ("Start process time: " + str(startProcessTime))
        #print ('Loop process time: '+str(tinyProcessTime))
        #print ("process time: "+str(processTime))
        #print ("Sleep time: " + str(sleepTime))
        
        
        sleepTime = 60 - (endTime.second-currentTime.second) - timeOffset
        
        time.sleep(sleepTime)
        
startAutobot()
startOfferTracker()
##Multiprocessing turned off for the moment
#if __name__ == '__main__':
    #Process(target=startOfferTracker).start()
    #Process(target=startAutobot).start()
    
@client.on(events.NewMessage(incoming=True, chats='cwsex'))
def message_handler(event):
    print(event)
    event.forward_to(proxy_chan_id)



