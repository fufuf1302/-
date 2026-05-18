
import os
import requests
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    yandex_id = db.Column(db.String(100), unique=True, nullable=False)
    context = db.Column(db.String(50), default='main_menu')  # Критерий: Контекст
    exp = db.Column(db.Integer, default=0)
    last_action = db.Column(db.String(100))

    def __repr__(self):
        return f'<User {self.yandex_id}>'

with app.app_context():
    db.create_all()


NASA_API_URL = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"


IMAGE_SPACE_ID = "937455/886027a475d9e5786720"
SOUND_ROCKET = "<speaker audio='alice-sounds-transport-ship-1.opus'>"


def get_nasa_data():
    try:
        response = requests.get(NASA_API_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logging.error(f"Error fetching NASA API: {e}")
    return None


def handle_dialog(event, res):
    user_id = event['session']['user_id']
    

    user = User.query.filter_by(yandex_id=user_id).first()
    if not user:
        user = User(yandex_id=user_id)
        db.session.add(user)
        db.session.commit()


    if event['session']['new']:
        user.context = 'main_menu'
        db.session.commit()
        res['response']['text'] = f"Привет, Космонавт! {SOUND_ROCKET} Я твой бортовой компьютер. Что хочешь узнать?"
        res['response']['buttons'] = get_buttons(user.context)
        return


    command = event['request']['command'].lower()
    

    if 'выход' in command or 'стоп' in command:
        res['response']['text'] = "До встречи в открытом космосе!"
        res['response']['end_session'] = True
        return

    if user.context == 'main_menu':
        if 'фото' in command or 'космос' in command:
            data = get_nasa_data()
            if data:
                res['response']['text'] = f"Сегодня в космосе: {data.get('title')}. Рассказать подробнее?"
                res['response']['card'] = {
                    "type": "BigImage",
                    "image_id": IMAGE_SPACE_ID,
                    "title": data.get('title'),
                    "description": "Фото дня от NASA загружено!"
                }
                user.context = 'viewing_photo'
                user.exp += 10 
            else:
                res['response']['text'] = "Связь с центром управления NASA прервана. Попробуй позже."
        
        elif 'статистика' in command:
            res['response']['text'] = f"Твой уровень подготовки: {user.exp} очков опыта."
            
        else:
            res['response']['text'] = "Я тебя не понял. Мы можем посмотреть фото дня или проверить твою статистику."

    elif user.context == 'viewing_photo':
        if 'да' in command or 'подробнее' in command:
            res['response']['text'] = "Это потрясающий вид! Возвращаемся в меню."
            user.context = 'main_menu'
        else:
            res['response']['text'] = "Хорошо, возвращаемся в главное меню."
            user.context = 'main_menu'

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


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
