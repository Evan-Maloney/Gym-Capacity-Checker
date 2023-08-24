from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request
from dotenv import dotenv_values


config = dotenv_values(".env")

account_sid = config["SID"]
auth_token = config["TOKEN"]

twilio_phone_number = config['TWILIO_PHONE']
your_phone_number = config['MY_PHONE']


app = Flask(__name__)


def smsSender():
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body='Capacity dropped below 60%!',
        from_=twilio_phone_number,
        to=your_phone_number
    )
    print('SMS notification sent!')

def checkCapacity():
    previous_capacity = None
    notifications_enabled = True
    
    while notifications_enabled:
        capacity = getCapacity()
        
        if capacity is not None:
            if previous_capacity is not None and capacity < 60 and previous_capacity >= 60:
                smsSender()
            
            previous_capacity = capacity
        
        time.sleep(300) 

def handle_incoming_message(message_body):
    if message_body.lower() == 'worked out!':
        global notifications_enabled
        notifications_enabled = False
        print('Notifications and functionality stopped.')

app.route('/sms', methods=['POST'])
def getSms():
    message_body = request.form['Body']
    handle_incoming_message(message_body)
    
    twiml_response = MessagingResponse()
    return str(twiml_response)

def getCapacity():
    webdriver_path = '/path/to/chromedriver'

    options = Options()

    options.add_argument('--headless') 

    driver = webdriver.Chrome(service=Service(executable_path=webdriver_path), options=options)

    url = 'https://goldsgymbc.ca/ubc-gym'
    driver.get(url)
    span_element = driver.find_element(By.ID, 'livecapacity')

    if span_element:
        print(span_element.text)
    else:
        print("Element not found")

    driver.quit()


if __name__ == '__main__':
    checkCapacity()