import requests
from json import loads

data = {}
# User1 Asia/Yekaterinburg, User2 Europe/Moscow
data['username'] = 'User1'  # 'User2'
data['date'] = '07/12/20'  # '%d/%m/%y'
data['start'] = '14:15'  # '%H:%M'
data['finish'] = '15:00'  # '%H:%M'
data['place_type'] = 'Workplace'  # 'Room'
# place_id можно узнать из расписания, сделав запрос на все места такого типа
data['place_id'] = '1'

fetch_data = {}
fetch_data['place_type'] = 'Workplace'  # 'Room'
# fetch_data['date'] = '08/12/20'
# fetch_data['place_id'] = '85'

# Данные для авторизации
auth_data={'username':'User1'}
# Данные для получения названия комнат
room_data={'place_type':'Workplace'} #Room


# Сюда стучимся бронировать, код 200 - успех, код 400 - ошибка
# Формат вызова виден выше, старт не раньше 09:00, финиш не позже 22:00
book_url = 'http://127.0.0.1:8000/telega/book'
# Сюда за расписанием. Либо всех мест/переговрок, либо по дате и/или айди конкретного места
# Формат ответа - строки вида '{Место}#{id} at {дата} from {начало} to {конец} by {юзернейм}, {часовой пояс}'
# Строки соритрованы по дате
fetch_url = 'http://127.0.0.1:8000/telega/fetch'

# урл для авторизации
auth_url ='http://127.0.0.1:8000/telega/auth'

#урл для получения названия комнат
fetch_room_url = 'http://127.0.0.1:8000/telega/fetch/rooms'
# если код ответа =200, то пользователь есть в бд

# Код ответа
# response = requests.post(book_url, data)
# JSON ответа
# print(loads(response.json()))
