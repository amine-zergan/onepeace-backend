from vonage import Client, Sms
import os
from random import randint




client = Client(key="3a465e27",secret="sPftKhIPf2THRgMx")

sms = Sms(client=client)

def send_message(phone:int,date:str):
    response= sms.send_message(
        {
        "from": "O.P.patient",
        "to": f"216{phone}",
        "text": f"your appointment is validate and will be :{date}",
    }
    )
    if response["messages"][0]["status"] == "0":
        print("message envoye")
        return "Message sent successfully."
    else:
        print(response['messages'][0]['error-text'])
        return f"Message failed with error: {response['messages'][0]['error-text']}"


    """This function for sending sms to user to send code verification
    using api called Vonage : 
    this package let us send message with api implimentation : 
    first you havee un idToken PI_SECRET_VONAGE , with importing module Client and Sms 
    after registration user recived code to confirmat there phone number 
    """