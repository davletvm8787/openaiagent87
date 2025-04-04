import openai
import sqlite3
import requests
import pdfplumber
import json
import speech_recognition 
import gTTS
from asyncio import Translator

# Инициализируем OpenAI клиента
client = openai.OpenAI()
translator = Translator()

# 🔍 Функция для веб-поиска
def web_search(query):
    """Выполняет веб-поиск и возвращает краткие результаты."""
    response = requests.get(f"https://api.searchengine.com?q={query}")
    return response.text[:500]  

# 📄 Функция для чтения PDF
def read_pdf(file_path):
    """Открывает PDF и извлекает текст."""
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return text[:1000]  

# 🗄️ Функция для работы с базой данных
def query_database(db_path, query):
    """Выполняет SQL-запрос в базе данных SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

# 📝 Генерация текста с помощью OpenAI
def generate_text(prompt):
    """Создает текст (например, статью или email) с помощью AI."""
    response = client.beta.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

# 🌍 Перевод текста
def translate_text(text, dest_language="en"):
    """Переводит текст на указанный язык."""
    translated = translator.translate(text, dest=dest_language)
    return translated.text

# ☁️ Получение данных о погоде через API
def get_weather(city):
    """Получает текущую погоду в указанном городе."""
    api_key = "ТВОЙ_API_КЛЮЧ"  # Используй свой ключ для OpenWeatherMap
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = json.loads(response.text)
    if data.get("main"):
        return f"Температура в {city}: {data['main']['temp']}°C, {data['weather'][0]['description']}"
    return "Не удалось получить данные о погоде."

# 🎙️ Голосовой ввод
def speech_to_text():
    """Преобразует голос в текст с помощью SpeechRecognition."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Говорите...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        return text
    except sr.UnknownValueError:
        return "Не удалось распознать речь."
    except sr.RequestError:
        return "Ошибка запроса к сервису распознавания."

# 🔊 Голосовой ответ
def text_to_speech(text, lang="ru"):
    """Преобразует текст в речь и сохраняет в MP3-файл."""
    tts = gTTS(text=text, lang=lang)
    tts.save("response.mp3")
    return "Аудио сохранено как response.mp3"

# 🧠 Создаем агента
agent = client.beta.agents.create(
    name="SmartAssistant",
    instructions="Ты многофункциональный AI-помощник, умеющий искать информацию, анализировать файлы, работать с БД, переводить и говорить.",
    tools=[
        {"name": "web_search", "function": web_search},
        {"name": "read_pdf", "function": read_pdf},
        {"name": "query_database", "function": query_database},
        {"name": "generate_text", "function": generate_text},
        {"name": "translate_text", "function": translate_text},
        {"name": "get_weather", "function": get_weather},
        {"name": "speech_to_text", "function": speech_to_text},
        {"name": "text_to_speech", "function": text_to_speech}
    ]
)

print("Агент успешно обновлен с новыми функциями!")
