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

        if request == 'поиск':
            db_func.create_or_clear_database()
            age_from, age_to, sex, city_title, city_id = bot_func.chat_bot(user_id)
            search_completed = True
            bot_func.sending_messages(user_id, f'Поиск завершен, для показа введите смотреть')

        elif request == 'смотреть':
            if search_completed:
                bot_func.sending_messages(user_id, f"offset = {offset}")
                bot_func.sending_messages(user_id, "Смотрим")
                bot_func.found_people(user_id=user_id, age_from=age_from, age_to=age_to, sex=sex, city_title=city_title, city_id=city_id, offset=offset)
                offset += 10
            else:
                bot_func.sending_messages(user_id, f'Сначала нужно ввести поиск')


        elif request == 'очистка':
            db_func.create_or_clear_database()



