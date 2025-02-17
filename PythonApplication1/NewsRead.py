import requests
import json
import pyttsx3

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)
engine.setProperty("rate", 170)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def latestnews():
    api_dict = {"business":"https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=54e095372ece4ee4be24987146c5973d",
              "entertainment":"https://newsapi.org/v2/top-headlines?country=in&category=entertainment&apiKey=54e095372ece4ee4be24987146c5973d",
              "health":"https://newsapi.org/v2/top-headlines?country=in&category=health&apiKey=54e095372ece4ee4be24987146c5973d",
              "science":"https://newsapi.org/v2/top-headlines?country=in&category=science&apiKey=54e095372ece4ee4be24987146c5973d",
              "sports":"https://newsapi.org/v2/top-headlines?country=in&category=sports&apiKey=54e095372ece4ee4be24987146c5973d",
              "technology":"https://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey=54e095372ece4ee4be24987146c5973d"}
    content = None
    url = None
    speak("which field news do you want to here, [business], [health], [science], [technology], [entertainment], [sports]")
    field = input("Type the field news that you want:")
    for key,value in api_dict.items():
        if key.lower() in field.lower():
            url = value
            print(url)
            print("here's some latest news...")
            break
        
        else:
            url = True
            
    if url is True:
        print("url not found")
                
    news = requests.get(url).text
    news = json.loads(news)
    speak("Here is the first news")
    
    arts = news["articles"]
    for articles in arts:
        article = articles["title"]
        print(article)
        speak(article)
        news_url = articles["url"]
        print("for more info visit: {news_url}")
        
        a = input("[press 1 to continue] and [press 2 to stop]")
        if str(a) == "1":
            pass
        elif str(a) == "2":
            break
            speak("thats all")
        