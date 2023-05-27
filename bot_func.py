from random import randrange
from bot import group_token
from bot import user_token
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
from db_func import add_user_to_table
from db_func import is_user_in_database


vk_group = vk_api.VkApi(token=group_token)
vk_group_got_api = vk_group.get_api()

vk_user = vk_api.VkApi(token=user_token)
vk_user_got_api = vk_user.get_api()

longpoll = VkLongPoll(vk_group)


def get_user_info(user_id):
    user_info = vk_group.method('users.get', {'user_ids': user_id, 'fields': 'sex,bdate,city,country'})
    return user_info


def sending_messages(user_id, message):
    vk_group_got_api.messages.send(user_id=user_id, message=message, random_id=randrange(10 ** 7))


def chat_bot(user_id, longpoll):
    user_info = get_user_info(user_id)

    age_from, age_to = get_age(user_id, user_info, longpoll)
    sex = get_sex(user_id, user_info)
    city_id, city_title = get_city(user_id, user_info, longpoll)

    return age_from, age_to, sex, city_title, city_id


def get_age(user_id, user_info, longpoll):
    sending_messages(user_id, f'Введите 1 - чтобы использовать Ваш возраст и введите 2 - чтобы ввести возраст вручную')
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text
            if request == '1':
                age_from, age_to = get_your_age(user_id, user_info)
                return age_from, age_to
            elif request == '2':
                age_from, age_to = get_new_age(user_id, longpoll)
                return age_from, age_to


def get_your_age(user_id, user_info):
    try:
        birthday = user_info[0]['bdate']
        birthdate = datetime.datetime.strptime(birthday, '%d.%m.%Y')
        today = datetime.datetime.now()
        age = (today - birthdate).days // 365
        sending_messages(user_id, f'Ваш возраст: {age}')
        return age, age
    except KeyError:
        sending_messages(user_id, f'У вас скрыта информация о вашем возрасте, перенаправляю на ввод возраста вручную')
        age_from, age_to = get_new_age(user_id, longpoll)
        return age_from, age_to


def get_new_age(user_id, longpoll):
    sending_messages(user_id, f'Введите минимальный возраст для поиска: ')
    min_age = None
    max_age = None
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if min_age is None:
                min_age = event.text
                if not min_age.isdigit() or int(min_age) < 16 or int(min_age) > 65:
                    sending_messages(user_id,
                                     'Некорректный минимальный возраст. Пожалуйста, введите число от 16 до 65:')
                    min_age = None
                else:
                    sending_messages(user_id, f'Минимальный возраст: {min_age}')
                    sending_messages(user_id, f'Введите максимальный возраст для поиска: ')
            elif max_age is None:
                max_age = event.text
                if not max_age.isdigit() or int(max_age) < 16 or int(max_age) > 65 or int(max_age) < int(min_age):
                    sending_messages(user_id, 'Некорректный максимальный возраст. '
                                              'Пожалуйста, введите число от 16 до 65 и '
                                              'больше или равное минимальному возрасту:')
                    max_age = None
                else:
                    sending_messages(user_id, f'Максимальный возраст: {max_age}')
                    return int(min_age), int(max_age)


def get_sex(user_id, user_info):
    user_sex = user_info[0]['sex']
    if user_sex == 1:
        sending_messages(user_id, f'Вы женщина, ищем мужчину!')
        return 2
    elif user_sex == 2:
        sending_messages(user_id, f'Вы мужчина, ищем женщину!')
        return 1


def get_city(user_id, user_info, longpoll):
    if 'city' in user_info[0]:
        city_id = user_info[0]['city']['id']
        city_title = user_info[0]['city']['id']

        sending_messages(user_id, f'Ищем в городе {city_title}')
        return city_id, city_title

    else:
        sending_messages(user_id, f'Введите название города:')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer = event.text.lower()
                cities = vk_user_got_api.database.getCities(
                        country_id=1, q=answer.capitalize(), need_all=1, count=1000
                    )["items"]
                for city in cities:
                    if city['title'] == answer.capitalize():
                        city_id = city['id']
                        city_title = city['title']
                        sending_messages(user_id, f'Ищем в городе: {city_title}')
                        return city_id, city_title
                else:
                    sending_messages(user_id, f'Город не найден, попробуйте еще раз')


def found_people(user_id, age_from, age_to, city_id, sex, city_title, offset):
    result = vk_user_got_api.users.search(
        count=30,
        offset=offset,
        city=city_id,
        age_from=age_from,
        age_to=age_to,
        sex=sex,
        status=6,
        has_photo=1,
        fields='is_closed, can_write_private_message, bdate, city'
    )

    sending_messages(user_id, f'Поиск успешен ')
    for user in result['items']:
        if user['is_closed'] == False and user['can_write_private_message'] == True:
            try:
                # user_profile = []

                user_url = f"https://vk.com/id{user['id']}"
                first_name = user['first_name']
                last_name = user['last_name']
                vk_id = user['id']
                user_bdate = user['bdate']

                if not is_user_in_database(vk_id):
                    user_photo = get_photo(user_id, user)
                    # user_profile.extend([first_name, last_name, user_url, user_photo])
                    # sending_messages(user_id, user_profile)

                    message = f"Имя: {first_name}\nФамилия: {last_name}\nГород: {city_title}\nСсылка на профиль: {user_url}\nДата рождения: {user_bdate}\nФотографии: {' '.join(user_photo)}"
                    sending_messages(user_id, message)

                    add_user_to_table(id_vk=vk_id)
            except vk_api.exceptions.ApiError as e:
                if e.code == 30:
                    sending_messages(user_id, f'Ошибка {e}')
                    continue

    sending_messages(user_id, f'Поиск завершен')


def get_photo(user_id, user):
    photos = vk_user_got_api.photos.get(
        owner_id=user['id'],
        album_id='profile',
        extended=1,
        count=3,
        sort='-likes,-comments'
    )

    user_photo = []

    for photo in photos['items']:
        user_photo.append(photo['sizes'][-1]['url'])
    return user_photo




















