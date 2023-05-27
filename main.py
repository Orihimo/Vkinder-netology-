from bot import group_token
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import bot_func
import db_func

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)

offset = 0
search_completed = False

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text
        user_id = event.user_id

        if request == 'старт':
            db_func.create_or_clear_database()
            age_from, age_to, sex, city_title, city_id = bot_func.chat_bot(user_id, longpoll)
            search_completed = True
            offset = 0
            bot_func.sending_messages(user_id, f'Данные пользователя созданы, для показа введите смотреть')

        elif request == 'смотреть':
            if search_completed:
                # if age_from is not None and age_to is not None and sex is not None and city_title and city_id: (Можно использовать и такую конструкцию, смысл будет один)
                if all([age_from, age_to, sex, city_title, city_id]):
                    bot_func.sending_messages(user_id, f"offset = {offset}")
                    bot_func.sending_messages(user_id, "Смотрим")
                    bot_func.found_people(user_id=user_id, age_from=age_from, age_to=age_to, sex=sex, city_title=city_title, city_id=city_id, offset=offset)
                    offset += 30
                else:
                    bot_func.sending_messages(user_id,
                                              f'Не все данные определены. Сначала нужно выполнить команду "старт"')
            else:
                bot_func.sending_messages(user_id, f'Сначала нужно ввести поиск')

        elif request == 'очистка':
            db_func.create_or_clear_database()
            bot_func.sending_messages(user_id, f'База очищена')

        else:
            bot_func.sending_messages(user_id, f"Введите 'старт' - для начала работы\n"
                                               f"Введите 'смотреть - для показа результатов\n"
                                               f"Введите 'очитска - чтобы очистить базу данных")




