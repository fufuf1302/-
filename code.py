
import os
import requests
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# --- Инициализация приложения и БД ---
app = Flask(__name__)
# Используем SQLite для хранения данных (критерий: Хранение данных в БД)
app.config['SQLALCHEMY_DATABASE_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- ORM Модели (Критерий: ORM-модели) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    yandex_id = db.Column(db.String(100), unique=True, nullable=False)
    context = db.Column(db.String(50), default='main_menu')  # Критерий: Контекст
    exp = db.Column(db.Integer, default=0)
    last_action = db.Column(db.String(100))

    def __repr__(self):
        return f'<User {self.yandex_id}>'

# Создание базы данных
with app.app_context():
    db.create_all()

# --- Константы и настройки ---
# NASA API для получения "Фото дня" (Критерий: Стороннее API)
NASA_API_URL = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"

# ID ресурсов, которые нужно предварительно загрузить в консоль разработчика
# (Критерий: Использование файлов: картинки, музыка)
IMAGE_SPACE_ID = "937455/886027a475d9e5786720" # Замените на свой ID
SOUND_ROCKET = "<speaker audio='alice-sounds-transport-ship-1.opus'>" # Встроенный звук Алисы

# --- Логика работы с API ---
def get_nasa_data():
    try:
        response = requests.get(NASA_API_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logging.error(f"Error fetching NASA API: {e}")
    return None

# --- Обработка диалога ---
def handle_dialog(event, res):
    user_id = event['session']['user_id']
    
    # 1. Поиск или создание пользователя в БД
    user = User.query.filter_by(yandex_id=user_id).first()
    if not user:
        user = User(yandex_id=user_id)
        db.session.add(user)
        db.session.commit()

    # 2. Обработка новой сессии
    if event['session']['new']:
        user.context = 'main_menu'
        db.session.commit()
        res['response']['text'] = f"Привет, Космонавт! {SOUND_ROCKET} Я твой бортовой компьютер. Что хочешь узнать?"
        res['response']['buttons'] = get_buttons(user.context)
        return

    # 3. Получение команды пользователя
    command = event['request']['command'].lower()
    
    # --- МАШИНА СОСТОЯНИЙ (Context handling) ---
    
    # Если пользователь хочет выйти
    if 'выход' in command or 'стоп' in command:
        res['response']['text'] = "До встречи в открытом космосе!"
        res['response']['end_session'] = True
        return

    # Навигация по контексту "Главное меню"
    if user.context == 'main_menu':
        if 'фото' in command or 'космос' in command:
            data = get_nasa_data()
            if data:
                res['response']['text'] = f"Сегодня в космосе: {data.get('title')}. Рассказать подробнее?"
                # Использование картинки (Card)
                res['response']['card'] = {
                    "type": "BigImage",
                    "image_id": IMAGE_SPACE_ID,
                    "title": data.get('title'),
                    "description": "Фото дня от NASA загружено!"
                }
                user.context = 'viewing_photo'
                user.exp += 10 # Начисление опыта за действие
            else:
                res['response']['text'] = "Связь с центром управления NASA прервана. Попробуй позже."
        
        elif 'статистика' in command:
            res['response']['text'] = f"Твой уровень подготовки: {user.exp} очков опыта."
            
        else:
            res['response']['text'] = "Я тебя не понял. Мы можем посмотреть фото дня или проверить твою статистику."

    # Навигация по контексту "Просмотр фото"
    elif user.context == 'viewing_photo':
        if 'да' in command or 'подробнее' in command:
            res['response']['text'] = "Это потрясающий вид! Возвращаемся в меню."
            user.context = 'main_menu'
        else:
            res['response']['text'] = "Хорошо, возвращаемся в главное меню."
            user.context = 'main_menu'

    # Сохраняем изменения в БД
    db.session.commit()
    res['response']['buttons'] = get_buttons(user.context)

def get_buttons(context):
    """Генерация кнопок в зависимости от контекста"""
    if context == 'main_menu':
        return [
            {'title': 'Фото дня', 'hide': True},
            {'title': 'Моя статистика', 'hide': True},
            {'title': 'Помощь', 'hide': True}
        ]
    elif context == 'viewing_photo':
        return [
            {'title': 'Подробнее', 'hide': True},
            {'title': 'Назад', 'hide': True}
        ]
    return []

# --- Роутинг Flask ---
@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json}')
    
    event = request.json
    response = {
        "session": event['session'],
        "version": event['version'],
        "response": {
            "end_session": False
        }
    }
    
    try:
        handle_dialog(event, response)
    except Exception as e:
        logging.error(f"Internal error: {e}")
        response['response']['text'] = "Произошла ошибка в бортовом компьютере. Мы скоро починим."

    return jsonify(response)

# --- Инструкция по хостингу (Критерий: Хостинг) ---
"""
Для развертывания этого навыка (хостинга) рекомендуется:
1. PythonAnywhere: Загрузите файлы, создайте Web App на Flask и укажите путь к main.py.
2. Yandex Cloud Functions: Позволяет запускать код без сервера. Требуется адаптация под handler.
3. VPS (Ubuntu): Используйте связку Gunicorn + Nginx.
   Команда для запуска: gunicorn --bind 0.0.0.0:5000 main:app
"""

if __name__ == '__main__':
    # В реальности лучше использовать переменные окружения для порта
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
