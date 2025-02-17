import pyttsx3
import datetime

engine = pyttsx3.init("sapi5")

voices = engine.getProperty("voices")
engine.setProperty("voice",voices[1].id)
engine.setProperty("rate",140)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()
        
def greetMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<=12:
        speak("good morning sir")
    elif hour>12 and hour<=18:
        speak("good afternoon sir")
        
    else:
        speak("good evening sir")
        
    speak("please tell me how can i help you")
    

    
    