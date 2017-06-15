import place_searcher_bot
import telepot

from telepot.loop import MessageLoop

admin_channel = -235455346
# slave_food_bot = telepot.Bot('382294505:AAHJ-9VomsZ8NPyVi2VU4PiPdrKKGARhdc4')
slave_food_bot = telepot.Bot('224991653:AAFvbFgD5WxF6o3dERRT7antDkjd_djH-U4')

APOLOGY = "Mohon tunggu beberapa saat, tryan sedang sibuk di kamar mandi"


def handle_food_bot(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if chat_id == admin_channel:
        return handle_admin_food_bot(msg)

    message = ""
    response = ""
    username = msg["from"]["first_name"]
    if content_type == 'text':
        message = msg["text"]
        response = place_searcher_bot.answer(chat_id, content_type, message)

    elif content_type == 'location':
        location = msg["location"]
        message = str(location)
        response = place_searcher_bot.answer(chat_id, content_type, location)

    if response == place_searcher_bot.UNKNOWN_RESPONSE:
	print(msg)
        slave_food_bot.forwardMessage(admin_channel, chat_id, msg["message_id"])
        response = APOLOGY

    print(str(chat_id) + ", From " + username + " got message " + message + " got response " + response)
    slave_food_bot.sendMessage(chat_id, response)


def handle_admin_food_bot(msg):
    print(msg)
    chat_id = msg['reply_to_message']['forward_from']['id']
    response = msg['text']
    slave_food_bot.sendMessage(chat_id, response)
    username = msg["from"]["first_name"]
    print(str(chat_id) + ", From " + username + " handled by admin with response " + response)


def debug_handle(msg):
    print(msg)


def start():
    MessageLoop(slave_food_bot, handle_food_bot).run_as_thread()
    print ('Food Bot Listening ...')
