from bot import group_token
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import bot_func
import db_func

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text
        user_id = event.user_id

        if request == 'поиск':
            db_func.create_or_clear_database()
            bot_func.chat_bot(user_id)

        elif request == 'смотреть':
            pass

        elif request == 'очистка':
            db_func.create_or_clear_database()

        # else:
        #     bot_func.sending_messages(user_id,
        #                               'Введите 1 или поиск для очистки бд и поиска новых знакомств, 2 или смотреть для просмотра результатов поиска, 3 или очистка для очистки бд')


