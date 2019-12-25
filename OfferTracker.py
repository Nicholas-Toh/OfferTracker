import pika
import json
import sys
import time

username = "admon_cwoffers_tracker"
password = "7AiXjEM8bm9BKuxurBbiXw8U3tZYvPAB"
chatid = 362348668
token = "9fbbf622098d3cbcd5065420b63fced6"
ignID = "53f3e27a124e01dcdd77de45995bf0db"
uuid= "bctps17qqm6hqta7ldhg"
code = "835782"
requestId = "bctps17qqm6hqta7ldhg"
myId = 323232619
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
                    #"token": token,
                    #"action": "requestProfile"
                    "action": "grantToken",
                    "payload": {
                        "userId": myId, #subjects Telegram userId
                        "authCode": code #authorization code, entered by user
                    }
                    }
                    #"payload": {  
                        #"requestId": uuid, #requestId of parent authAdditionalOperation 
                        #"authCode": code #code supplied by user for this requestId  

        
        
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
            #print (newProfile["payload"]["profile"]["stamina"])
            return newProfile

            
        
    def sort_info(self, channel, method_frame, header_frame, body):
        #print (method_frame.delivery_tag)
        print (body)
        self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        self.offerdict = self.convert_Json_to_Body(body)
        #print (offerdict)
        self.item = self.offerdict["item"]
        self.seller = self.offerdict["sellerName"] 
        self.price = self.offerdict["price"]
        try:
            print (self.item)
            print (self.price)
        except UnicodeEncodeError:
            #startProcessTime = time.process_time()
            self.item = self.item[1:]
            #endProcessTime = time.process_time()
            #print (endProcessTime-startProcessTime)
            print (self.item)
            print (self.price)
            #requests.get(website+"/sendmessage?chat_id="+str(chatid)+"&text= Item: "+ item + ", Seller: " + seller + ", price: "+str(price))
        self.check_item(self.item)
    
    def check_item(self, item):
        if item == "Scroll of Rage" or item == "Scroll of Peace":
            print ("Found "+item)
            return True
        
    def start(self):
        self.establish_connection()
        self.create_channel()
        self.publish(self.options[1])
        self.begin_consume()

trackOffers = OfferTracker(username, password)
trackOffers.start()
