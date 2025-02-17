import os
import webbrowser
import pyttsx3
from time import sleep
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import speech_recognition as sr

from time import sleep

engine = pyttsx3.init("sapi5")

voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)
engine.setProperty("rate", 170)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()
    
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.energy_threshold = 400
        audio = r.listen(source, timeout=5, phrase_time_limit=5)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"You said: {query}\n")
        return query.lower()
    except Exception as e:
        print("Error recognizing speech:", str(e))
        return ""


dictapp = {
    "commandprompt": "cmd",
    "paint": "mspaint",
    "word": "winword",
    "excel": "excel",
    "chrome": "chrome",
    "vscode": "code",
    "powerpoint": "powerpnt",
}

def openappweb(query):
    speak("Opening, sir.")

    if any(kw in query for kw in [".com", ".co.in", ".org", ".net"]):
        # Clean up the query and build the URL
        query = query.replace("open", "")
        query = query.replace("jarvis", "")
        query = query.replace("launch", "")
        query = query.strip()  # Remove any extra spaces
        
        # Construct the full URL and open it in the web browser
        url = f"https://www.{query}"
        webbrowser.open(url)
    elif "chat" in query:
        # Open ChatGPT website
       webbrowser.open("https://chat.openai.com")  # Open ChatGPT demo page
        
        # Interact with ChatGPT using voice commands
        
    else:
        # If it's not a website or ChatGPT, check if it's an application
        keys = list(dictapp.keys())
        for app in keys:
            if app in query:
                os.system(f"start {dictapp[app]}")


def closeappweb(query):
    speak("Closing, sir.")
    num_tabs = 0

    # Check how many tabs to close based on the query
    if "one tab" in query or "1 tab" in query:
        num_tabs = 1
    elif "two tabs" in query or "2 tabs" in query:
        num_tabs = 2
    elif "three tabs" in query or "3 tabs" in query:
        num_tabs = 3
    elif "four tabs" in query or "4 tabs" in query:
        num_tabs = 4
    elif "five tabs" in query or "5 tabs" in query:
        num_tabs = 5

    # Close the tabs
    if num_tabs > 0:
        for _ in range(num_tabs):
            pyautogui.hotkey("ctrl", "w")
            sleep(0.5)
        speak("All tabs closed.")
    else:
        # If it's not about closing tabs, check for apps to close
        keys = list(dictapp.keys())
        for app in keys:
            if app in query:
                os.system(f"taskkill /f /im {dictapp[app]}.exe")
