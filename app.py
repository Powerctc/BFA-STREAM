import os
import time
import threading
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GitHub Secrets ထဲက BOT_TOKEN ကို ဖတ်ခြင်း
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=False)

FOTMOV_DOWN_URL_4 = "https://t.me/BFASTREAMDownloader/6"
WEB_DOWN_URL_4 = "http://bfa-stream-apk-downloader.vercel.app"
DIRECT_WATCH_URL_4 = "https://bamarthan-one.vercel.app/"
TIKTOK_DOWN_URL_4 = "https://t.me/tknowatermarkdownloader"
ADMIN_GROUP_URL_4 = "https://t.me/addlist/AP4JevHUe7BkMDk1"
ADMIN_FB_URL_4 = "https://www.facebook.com/share/1D51YRzmjL/"
TIKTOK_SHOP_URL_4 = "https://vt.tiktok.com/ZS9jeujKenGgm-N6gSJ/"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        welcome_text = (
            "👋 **မင်္ဂလာပါ သယ်ရင်းရေ...**\n"
            "🚀 **BFA STREAM TV Official Bot** မှ ကြိုဆိုပါတယ်ဗျာ။\n\n"
            "👇 အောက်ပါ ခလုတ်များကို နှိပ်၍ အသုံးပြုနိုင်ပါပြီ -"
        )
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📥 BFA STREAM TV DOWN ရန်", url=FOTMOV_DOWN_URL_4),
            InlineKeyboardButton("📥 BFA STREAM TV DOWN ရန်", url=WEB_DOWN_URL_4),
            InlineKeyboardButton("🌐 iOS/PC/SMART တိုက်ရိုက်ကြည့်ရန်", url=DIRECT_WATCH_URL_4),
            InlineKeyboardButton("🎬 TikTok Video Downloader", url=TIKTOK_DOWN_URL_4),
            InlineKeyboardButton("🇹🇭 TikTok SHOP", url=TIKTOK_SHOP_URL_4),
            InlineKeyboardButton("👥 Admin Group/Channel", url=ADMIN_GROUP_URL_4),
            InlineKeyboardButton("👤 Admin FB Account", url=ADMIN_FB_URL_4)
        )
        bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)
    except Exception as e: logger.error(f"Welcome error: {e}")

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        if new_member.is_bot: continue
        try:
            text = f"👋 မင်္ဂလာပါ {new_member.first_name} ရေ!\nBFA STREAM TV Group မှ လှိုက်လှဲစွာ ကြိုဆိုပါတယ်ဗျာ။ ✨"
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("📥 BFA STREAM TV DOWN ရန်", url=FOTMOV_DOWN_URL_4),
                InlineKeyboardButton("🌐 iOS/PC/SMART တိုက်ရိုက်ကြည့်ရန်", url=DIRECT_WATCH_URL_4),
                InlineKeyboardButton("🎬 TikTok Video Downloader", url=TIKTOK_DOWN_URL_4),
                InlineKeyboardButton("🇹🇭 TikTok SHOP", url=TIKTOK_SHOP_URL_4)
            )
            bot_user = bot.get_me().username
            markup.add(InlineKeyboardButton("🤖 Bot စတင်ရန် (/start)", url=f"https://t.me/{bot_user}?start=start"))
            sent_msg = bot.send_message(message.chat.id, text, reply_markup=markup, disable_web_page_preview=True)
            
            def delete_msg():
                time.sleep(5)
                try: bot.delete_message(message.chat.id, sent_msg.message_id)
                except: pass
            threading.Thread(target=delete_msg, daemon=True).start()
        except Exception as e: logger.error(f"New member error: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_other_messages(message):
    try:
        if message.content_type != 'text': return
        bot.reply_to(message, "💡 BFA STREAM TV ဝန်ဆောင်မှုများ ရယူရန်အတွက် /start ဟု နှိပ်ပေးပါ သယ်ရင်း။")
    except Exception as e: logger.error(f"Message handler error: {e}")

if __name__ == "__main__":
    logger.info("Bot is starting with Long Polling...")
    # အဟောင်းက Webhook တွေကို ဖျက်ပြီး ပတ်ခိုင်းထားတဲ့အတွက် ပုံမှန်အတိုင်း မက်ဆေ့ခ်ျတွေ ချက်ချင်း ပြန်တုံ့ပြန်ပါလိမ့်မယ်
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
    
