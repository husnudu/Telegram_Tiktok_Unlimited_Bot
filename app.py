
# To Run the bot just do the following: 
# 1)add api token in the json file
# 2)rename the json file from (_api.json) to (api.josn)
#---------------------------------------------------------------
from typing import AnyStr
from moviepy.editor import *
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext, CallbackQueryHandler, messagequeue
from telegram.error import BadRequest, TimedOut
import os
from time import sleep as s
import zipfile

def isEnglish(s):
  return s.isascii()

def converter(output_name_from_user,outputfile):
    clip = VideoFileClip(output_name_from_user)
    clip.write_videofile(outputfile)

def hexChanger(Video_webm):
    video = Video_webm
    newBytes = b'\x88@\xb0}\xb0\x00'
    with open(video, 'rb') as f:
        content = f.read()
    f.close()    
    data = (bytearray(content))
    index = data.find(b'D\x89')
    index += 2
    data[index:index + 6] = newBytes
    with open(video, 'wb') as f2:
        f2.write(data)
        s(5)
    f2.close()
    os.remove(output_name_from_user)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send Me Your Video ...')
    seending(update, context)

def ask(update, context) -> None:
    keyboard = [[ InlineKeyboardButton(".webm", callback_data='(.Webm)'), InlineKeyboardButton(".Zip", callback_data='(.Zip)'),],]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Receive Video as What?', reply_markup = reply_markup)
    

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Sending video as : {query.data}")
    global ans
    ans = query.data   
    context.bot.send_message(update.effective_chat.id,"Send (F) to Continue...")
    dp.add_handler(MessageHandler(Filters.all, seending))
     

def seending(update: Update, context: CallbackContext) -> None:
    if ans is not None:
        str = "{}".format(update.message.text)
        if isEnglish(str) == True and str.upper() == "F":
            try:
                context.bot.sendChatAction(chat_id=update.message.chat_id , action = telegram.ChatAction.UPLOAD_VIDEO)
                s(3)
                if ans == '(.Webm)':
                    with open(outputfile, 'rb') as vid:
                        context.bot.send_document(chat_id = update.message.chat_id, document = vid, timeout=1000)
                elif ans == '(.Zip)':
                    zipf = "{}.zip".format(output_name_from_user[0:output_name_from_user.find('.')])
                    zf = zipfile.ZipFile(zipf, mode='w')
                    zf.write(outputfile, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
                    zf.close()
                    context.bot.send_document(chat_id = update.message.chat_id, document = open(zipf,'rb'), filename= zipf)
                    if os.path.exists(zipf):
                        os.remove(zipf)
                    else:
                        pass
                context.bot.send_message(update.effective_chat.id,"Done.")
                s(5)
                if os.path.exists(outputfile):
                    os.remove(outputfile)
                else:
                    pass
            except (BadRequest, NameError) as err:
                context.bot.send_message(update.effective_chat.id,"Sorry, Try again...")
                print(err)
        else:
            context.bot.send_message(update.effective_chat.id,"Send (F) to Continue...")
            dp.add_handler(MessageHandler(Filters.all, seending))
    else:
        context.bot.send_message(update.effective_chat.id,"Please Wait...")
        seending(update, context)

def video_handler(update: Update, context: CallbackContext) -> None:  
    try:    
        context.bot.sendChatAction(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
        s(3)
        context.bot.send_message(update.effective_chat.id,"Please Wait...")
        video = context.bot.getFile(update.message.video.file_id)
        global file_id
        file_id = update.message.video.file_id
        global output_name_from_user
        output_name_from_user = "{}'s_Video.mp4".format(update.message.from_user.username)
        video.download(output_name_from_user)
        global outputfile
        outputfile = "{}.webm".format(output_name_from_user[0:output_name_from_user.find('.')])
        converter(output_name_from_user, outputfile)
        hexChanger(outputfile)
        ask(update, context)
        
    except(BadRequest, TimeoutError,RuntimeError, TypeError, NameError) as err:
        context.bot.send_message(update.effective_chat.id,"Sorry, Try again...")
        print(err)


def main():
    with open('api.json') as jsonF:
        data = json.load(jsonF)
        global updater
        global dp
    updater = Updater("{}".format(data['botApiKey']), use_context=True, request_kwargs={'read_timeout': 1000, 'connect_timeout': 1000})
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))

    #calling video_handler function
    dp.add_handler(MessageHandler(Filters.video, video_handler))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()
    
if __name__ == "__main__":
    main()