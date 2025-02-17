import datetime
import pyttsx3
import speech_recognition as sr
import webbrowser
import wikipedia
import pywhatkit
import requests
from win10toast import ToastNotifier
import pyautogui
import os
import random
from bs4 import BeautifulSoup
from threading import Thread
import pygame
import time
from transformers import pipeline
import sqlite3
import bcrypt
import tkinter as tk
from PIL import Image, ImageTk
from gtts import gTTS
from DictApp import closeappweb, openappweb
from googletrans import Translator

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    revision="main"  # or a specific commit hash if you want to lock it down
)
# ----------------------------
# Database Functions
# ----------------------------
conn = sqlite3.connect('user_database.db')
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password BLOB
    )
""")
conn.commit()
conn.close()

def add_new_user(username, password):
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if not result:
        return False
    stored_hashed_pw = result[0]
    is_correct = bcrypt.checkpw(password.encode('utf-8'), stored_hashed_pw)
    conn.close()
    return is_correct

def change_password_in_db(username, new_password):
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    new_hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_hashed_pw, username))
    conn.commit()
    conn.close()

# ----------------------------
# User Login
# ----------------------------
for i in range(3):
    username = input("Enter username: ")
    password = input("Enter password: ")
    if verify_user(username, password):
        print("Welcome!")
        break
    else:
        print("Incorrect username or password. Try again.")
        if i == 2:
            print("Too many failed attempts. Exiting...")
            exit()

# ----------------------------
# Text-to-Speech & Greeting
# ----------------------------
engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)
engine.setProperty("rate", 140)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def greetMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good morning, sir")
    elif hour >= 12 and hour < 18:
        speak("Good afternoon, sir")
    else:
        speak("Good evening, sir")
    speak("Please tell me how can I help you")

# ----------------------------
# Voice Command Function
# ----------------------------
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.energy_threshold = 400
        audio = r.listen(source, timeout=4)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"You said: {query}\n")
        return query.lower()
    except Exception as e:
        print("Error recognizing speech:", str(e))
        return "none"

# ----------------------------
# Alarm Functions
# ----------------------------
def check_alarm():
    pygame.mixer.init()
    while True:
        try:
            with open("Alarmtext.txt", "r") as time_file:
                alarm_time = time_file.read().strip()
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            if alarm_time == current_time:
                speak("Alarm ringing!")
                pygame.mixer.music.load("music.mp3")
                pygame.mixer.music.play()
                break
            time.sleep(1)
        except FileNotFoundError:
            time.sleep(1)

def set_alarm_by_input():
    speak("Please enter the alarm time in HH:MM:SS format:")
    time_input = input("Enter the alarm time (HH:MM:SS): ")
    formatted_time = time_input.strip()
    try:
        datetime.datetime.strptime(formatted_time, "%H:%M:%S")
    except ValueError:
        speak("Invalid time format. Please use HH:MM:SS.")
        return
    with open("Alarmtext.txt", "w") as time_file:
        time_file.write(formatted_time)
    speak(f"Alarm set for {formatted_time}")

def start_alarm_thread():
    try:
        alarm_thread = Thread(target=check_alarm, daemon=True)
        alarm_thread.start()
    except Exception as e:
        speak("Could not start the alarm-checking process.")

# ----------------------------
# Other Functionalities
# ----------------------------
def searchGoogle(query):
    print("Searching Google for:", query)
    webbrowser.open_new_tab(f"https://www.google.com/search?q={query}")

def searchYoutube(query):
    print("Searching YouTube for:", query)
    webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={query}")
    pywhatkit.playonyt(query)

def searchWikipedia(query):
    print("Searching Wikipedia for:", query)
    try:
        result = wikipedia.summary(query.replace("wikipedia", ""), sentences=2)
        speak("According to Wikipedia...")
        print(result)
        speak(result)
    except wikipedia.exceptions.DisambiguationError:
        speak("There are multiple possible matches for this query. Please try again.")
    except wikipedia.exceptions.PageError:
        speak("Sorry, I couldn't find any relevant information on Wikipedia for this query.")

def speak_translated_text(text, language_code):
    tts = gTTS(text=text, lang=language_code)
    tts.save("translated_text.mp3")
    pygame.mixer.music.load("translated_text.mp3")
    pygame.mixer.music.play()

# ----------------------------
# Handler Functions for Additional Commands
# ----------------------------
def handle_change_password():
    speak("Please enter your username.")
    username = input("Enter your username: ")
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    user_exists = cursor.fetchone()
    conn.close()
    if user_exists:
        speak("What's the new password?")
        new_password = input("Enter the new password: ")
        change_password_in_db(username, new_password)
        speak(f"Password changed successfully for {username}")
    else:
        speak("Username not found. Please try again.")

def handle_add_new_password():
    speak("Please enter the new username.")
    new_username = input("Enter the new username: ")
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (new_username,))
    user_exists = cursor.fetchone()
    conn.close()
    if user_exists:
        speak(f"The username '{new_username}' already exists. Please choose a different one.")
    else:
        speak("What's the new password for this user?")
        new_password = input("Enter the new password: ")
    if add_new_user(new_username, new_password):
         speak(f"New user '{new_username}' added successfully.")
    else:
         speak(f"Failed to add new user '{new_username}'. Please try again.")

def handle_translate():
    language_codes = {
        'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar',
        'armenian': 'hy', 'azerbaijani': 'az', 'basque': 'eu', 'belarusian': 'be',
        'bengali': 'bn', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca',
        'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-CN',
        'chinese (traditional)': 'zh-TW', 'corsican': 'co', 'croatian': 'hr',
        'czech': 'cs', 'danish': 'da', 'dutch': 'nl', 'english': 'en',
        'esperanto': 'eo', 'estonian': 'et', 'filipino': 'tl', 'finnish': 'fi',
        'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka',
        'german': 'de', 'greek': 'el', 'gujarati': 'gu', 'haitian creole': 'ht',
        'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'iw', 'hindi': 'hi',
        'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig',
        'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja',
        'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km',
        'kinyarwanda': 'rw', 'korean': 'ko', 'kurdish (kurmanji)': 'ku',
        'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv',
        'lithuanian': 'lt', 'luxembourgish': 'lb', 'macedonian': 'mk',
        'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt',
        'maori': 'mi', 'marathi': 'mr', 'mongolian': 'mn', 'myanmar (burmese)': 'my',
        'nepali': 'ne', 'norwegian': 'no', 'odia': 'or', 'pashto': 'ps',
        'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa',
        'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'scots gaelic': 'gd',
        'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd',
        'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so',
        'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv',
        'tajik': 'tg', 'tamil': 'ta', 'telugu': 'te', 'thai': 'th',
        'turkish': 'tr', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug',
        'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh',
        'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'
    }
    speak("Enter the text you want to translate:")
    text_input = input("Enter the text to translate: ")
    speak("Enter the target language you want to translate in:")
    target_language = input("Enter the target language (e.g., French, Spanish, German): ")
    target_language = target_language.lower()
    target_language_code = language_codes.get(target_language, 'en')
    translator = Translator()
    try:
         translated_text = translator.translate(text_input, dest=target_language_code).text
         print("Translated text:", translated_text)
         speak_translated_text(translated_text, target_language_code)
    except Exception as e:
         print("Translation error:", str(e))
         speak("Sorry, I couldn't translate the text.")

def handle_temperature(query):
    words = query.split()
    try:
        index = words.index("temperature")
        city = " ".join(words[index + 2:])
        search = f"temperature in {city}"
        r = requests.get(f"https://www.google.com/search?q={search}")
        data = BeautifulSoup(r.text, "html.parser")
        temp = data.find("div", class_="BNeawe").text
        speak(f"Current temperature in {city} is {temp}")
    except Exception as e:
        speak("Sorry, I couldn't retrieve the temperature.")

def handle_weather(query):
    words = query.split()
    try:
        index = words.index("weather")
        city = " ".join(words[index + 2:])
        search = f"weather in {city}"
        r = requests.get(f"https://www.google.com/search?q={search}")
        data = BeautifulSoup(r.text, "html.parser")
        weather_info = data.find("div", class_="BNeawe").text
        weather_mood = weather_info.split(',')[0]
        speak(f"Current weather in {city} is {weather_mood}")
    except Exception as e:
        speak("Sorry, I couldn't retrieve the weather information.")

def handle_time():
    strTime = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {strTime}")

def handle_volume_up():
    from keyboard import volumeup
    speak("Turning volume up")
    volumeup()

def handle_volume_down():
    from keyboard import volumedown
    speak("Turning volume down")
    volumedown()

def handle_remember(query):
    rememberMessage = query.replace("remember that", "")
    speak("You told me to remember that " + rememberMessage)
    with open("remember.txt", "a") as remember_file:
         remember_file.write(rememberMessage)

def handle_recall():
    try:
        with open("remember.txt", "r") as remember_file:
            content = remember_file.read()
        speak("You told me to remember that " + content)
    except Exception as e:
        speak("I don't remember anything yet.")

def handle_news():
    from NewsRead import latestnews
    latestnews()

def handle_calculate(query):
    from CalculateNumbers import Calc
    modified_query = query.replace("calculate", "").replace("jarvis", "")
    Calc(modified_query)

def handle_shutdown():
    speak("Are you sure you want to shutdown?")
    shutdown = input("Do you wish to shutdown your computer? (yes/no): ")
    if shutdown.lower() == "yes":
         os.system("shutdown /s /t 1")
    elif shutdown.lower() == "no":
         speak("Shutdown aborted.")

def handle_schedule():
    tasks = []
    speak("Do you want to clear old tasks? Please speak YES or NO:")
    response = takeCommand().lower()
    if "yes" in response:
         with open("tasks.txt", "w") as file:
              file.write("")
         no_tasks = int(input("Enter the number of tasks: "))
         for i in range(no_tasks):
              task = input("Enter the task: ")
              tasks.append(task)
              with open("tasks.txt", "a") as file:
                   file.write(f"{i}. {task}\n")
    elif "no" in response:
         no_tasks = int(input("Enter the number of tasks: "))
         for i in range(no_tasks):
              task = input("Enter the task: ")
              tasks.append(task)
              with open("tasks.txt", "a") as file:
                   file.write(f"{i}. {task}\n")

def handle_show_schedule():
    toaster = ToastNotifier()
    try:
        with open("tasks.txt", "r") as file:
            content = file.read()
        toaster.show_toast(title="My Schedule :-", msg=content, duration=15, threaded=True)
    except Exception as e:
        speak("I don't have any scheduled tasks.")

def handle_rock_paper():
    from game import game_play
    game_play()

def handle_escape():
    maze = [
         [" ", "#", " ", " ", " ", "#"],
         [" ", "#", "#", "#", " ", "#"],
         [" ", " ", " ", "#", " ", " "],
         ["#", "#", " ", "#", "#", " "],
         [" ", " ", " ", " ", " ", "E"]
    ]
    print("Welcome to the Maze Escape Game!")
    print("Use 'W', 'A', 'S', 'D' keys to navigate. 'E' to exit.")
    player_position = (0, 0)
    while True:
        for row in maze:
            print("".join(row))
        move = input("Enter your move (W/A/S/D): ").upper()
        if move == "W" and player_position[0] > 0 and maze[player_position[0]-1][player_position[1]] != "#":
            player_position = (player_position[0]-1, player_position[1])
        elif move == "A" and player_position[1] > 0 and maze[player_position[0]][player_position[1]-1] != "#":
            player_position = (player_position[0], player_position[1]-1)
        elif move == "S" and player_position[0] < len(maze)-1 and maze[player_position[0]+1][player_position[1]] != "#":
            player_position = (player_position[0]+1, player_position[1])
        elif move == "D" and player_position[1] < len(maze[0])-1 and maze[player_position[0]][player_position[1]+1] != "#":
            player_position = (player_position[0], player_position[1]+1)
        elif move == "E" and maze[player_position[0]][player_position[1]] == "E":
            print("Congratulations! You escaped the maze!")
            break
        else:
            print("Invalid move. Try again.")
        maze[player_position[0]][player_position[1]] = "P"

def handle_word_guessing():
    words = ["python", "banana", "computer", "orange", "programming", "keyboard", "apple"]
    secret_word = random.choice(words)
    guessed_word = "_" * len(secret_word)
    attempts = 0
    max_attempts = 6
    print("Welcome to the Word Guessing Game!")
    print("Try to guess the hidden word.")
    while attempts < max_attempts:
        print("Current word:", guessed_word)
        guess = input("Enter a letter or guess the word: ").lower()
        if len(guess) == 1:
            if guess in secret_word:
                print("Correct guess!")
                guessed_word = "".join([char if char == guess or guessed_word[i] != "_" else "_" for i, char in enumerate(secret_word)])
            else:
                print("Incorrect guess. Try again.")
                attempts += 1
        elif guess == secret_word:
            print("Congratulations! You guessed the word correctly:", secret_word)
            return
        else:
            print("Incorrect guess. Try again.")
            attempts += 1
    if attempts == max_attempts:
        print("Sorry, you ran out of attempts. The word was:", secret_word)

def handle_hangman():
    words = ["apple", "banana", "cherry", "orange", "grape", "kiwi", "lemon"]
    secret_word = random.choice(words)
    guessed_letters = []
    max_attempts = 6
    attempts = 0
    print("Welcome to Hangman!")
    print("Try to guess the secret word.")
    while attempts < max_attempts:
        display_word = ""
        for letter in secret_word:
            if letter in guessed_letters:
                display_word += letter
            else:
                display_word += "_"
        print("Current word:", display_word)
        guess = input("Guess a letter: ").lower()
        if guess in guessed_letters:
            print("You already guessed that letter. Try again.")
        elif guess in secret_word:
            print("Correct guess!")
            guessed_letters.append(guess)
            if set(guessed_letters) == set(secret_word):
                print("Congratulations! You guessed the word:", secret_word)
                return
        else:
            print("Incorrect guess. Try again.")
            attempts += 1
    if attempts == max_attempts:
        print("Sorry, you ran out of attempts. The word was:", secret_word)

def handle_number_guessing():
    secret_number = random.randint(1, 100)
    print("Welcome to the Number Guessing Game!")
    print("I've picked a number between 1 and 100. Try to guess it!")
    attempts = 0
    while True:
        guess = int(input("Enter your guess: "))
        attempts += 1
        if guess < secret_number:
            print("Too low! Try again.")
        elif guess > secret_number:
            print("Too high! Try again.")
        else:
            print(f"Congratulations! You guessed the number {secret_number} in {attempts} attempts!")
            return

def handle_joke():
    jokes = [
         "Why don't scientists trust atoms? Because they make up everything!",
         "I'm reading a book on anti-gravity. It's impossible to put down!",
         "Parallel lines have so much in common. It's a shame they'll never meet.",
         "I told my wife she was drawing her eyebrows too high. She looked surprised.",
         "I'm reading a book about anti-gravity. It's really uplifting!",
         "Why did the scarecrow win an award? Because he was outstanding in his field!",
         "Why don't skeletons fight each other? They don't have the guts.",
         "Why did the bicycle fall over? Because it was two-tired!"
    ]
    joke = random.choice(jokes)
    speak(joke)

def exit_system():
    speak("Okay sir, you can call me anytime.")
    return "exit"

# ----------------------------
# Intent-Action Dictionary
# ----------------------------
INTENT_ACTIONS = {
    "wake up": lambda q: greetMe(),
    "change password": lambda q: handle_change_password(),
    "add new password": lambda q: handle_add_new_password(),
    "google": searchGoogle,
    "youtube": searchYoutube,
    "set alarm": set_alarm_by_input,
    "wikipedia": searchWikipedia,
    "hey there" : lambda q: (print("hey! nice to hear from you"), speak("hey! nice to hear from you")),
    "translate": lambda q: handle_translate(),
    "bye bye": lambda q: exit_system(),
    "hello": lambda q: (print("Hello!!!, how can i assist you?"), speak("Hello!, how can i assist you?")),
    "i am fine": lambda q: (print("Its nice that you are fine!"), speak("Its nice that you are fine!")),
    "how are you": lambda q: (print("I'm great! thanks for asking, how about you?"), speak("I'm great! thanks for asking, how about you?")),
    "open": openappweb,
    "close": closeappweb,
    "temperature": handle_temperature,
    "weather": handle_weather,
    "time": lambda q: handle_time(),
    "pause": lambda q: pyautogui.press("k"),
    "mute": lambda q: (pyautogui.press("m"), speak("video muted")),
    "volume up": handle_volume_up,
    "whats up" or "what's up": lambda q:(print("nothing, just here to assist you."), speak("nothing, just here to assist you.") ),
    "volume down": handle_volume_down,
    "remember that": handle_remember,
    "what do you remember": lambda q: handle_recall(),
    "news": lambda q: handle_news(),
    "calculate": handle_calculate,
    "shutdown the system": lambda q: handle_shutdown(),
    "schedule my day": lambda q: handle_schedule(),
    "show my schedule": lambda q: handle_show_schedule(),
    "rock paper": lambda q: handle_rock_paper(),
    "escape": lambda q: handle_escape(),
    "word guessing": lambda q: handle_word_guessing(),
    "hangman": lambda q: handle_hangman(),
    "number guessing": lambda q: handle_number_guessing(),
    "joke": lambda q: handle_joke()
}

# ----------------------------
# Main Loop
# ----------------------------
def main():
    start_alarm_thread()  # Start the alarm-checking thread
    while True:
        query = takeCommand().lower()
        if query == "none" or query.strip() == "":
            continue
        print("Received query:", query)
        handled = False
        for key, action in INTENT_ACTIONS.items():
            if key in query:
                result = action(query)
                handled = True
                if result == "exit":
                    return
                break
        if not handled:
            # Fallback: if no intent is matched, perform sentiment analysis and give a default response.
            from transformers import pipeline  # (Assuming it's already imported above)
            # Here, we use the global sentiment_analyzer
            
            result = sentiment_analyzer(query)[0]
            print(f"Sentiment: {result['label']}, Confidence: {result['score']:.2f}")
            speak("I'm not sure how to handle that, sir.")

if __name__ == "__main__":
    main()
