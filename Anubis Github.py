from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue, CallbackContext
import random

#Bot Configuration

TOKEN: Final = 'Your API TOKEN' 
BOT_USERNAME: Final ='BOT USERNAME'

# Verify if the command comes from a legit group and answer, Only answer if the message is sent in the following group.
async def pentesters_community(update):
    text: str = update.message.text
    if update.message.chat.id != -Your Chat ID: #Set your group chat ID.
        response: str = handle_response(text)
        print('Bot:', response)
        await update.message.reply_text(response)
        return True
    else:
        return False


#Captcha for the new group members.
async def send_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):

    updateMSG = getattr(update, "message", None)

    for user in updateMSG.new_chat_members:
        user_name= user.first_name

    chat_id=update.message.chat.id
    captcha_code = random.randint(1,999)
    #Saving variables into context, like the captcha code, userid and a counter.
    context.user_data['captcha' + str(update.message.from_user.id)] = captcha_code
    context.user_data['userID'+ str(update.message.from_user.id)] = update.message.from_user.id
    context.user_data['intentos'+ str(update.message.from_user.id)] = 3


    message=("👨‍💻 Hola "
                ""+ str(user_name) + ""
                ", con el fin de verificar tu identidad, envía el número que aparece a continuación:"
                "\n\n 🔴 El número es: "
                "" + str(captcha_code) + ""
                " 🔴"
                "\n\n En caso de no ser enviado correctamente, serás expulsado")
    captcha_message = await context.bot.send_message(chat_id, message) #We send the captcha
    context.user_data['message'+ str(update.message.from_user.id)] = captcha_message.message_id

#Checking if the user sent the captcha correctly.
async def check_captcha(update,context):

    user_code = update.message.text
    chat_id=update.message.chat.id
    user_id=update.message.from_user.id
    username = update.message.from_user.first_name

    ### Message sended in a private chat
    message_type: str = update.message.chat.type
    text: str = update.message.text
    print(f'User ({update.message.from_user.first_name}) in {message_type} {update.message.chat.id} : "{text}"')

    #Checking the chat, if is a private one, the bot doesn´t answer and recommends the community in which works:

    if message_type == 'private':
        response: str = handle_response(text)
        print('Bot:', response)
        await update.message.reply_text(response)

    # Captcha 
    if 'userID'+str(update.message.from_user.id) in context.user_data:
        if str(update.message.from_user.id) == str(context.user_data['userID'+ str(update.message.from_user.id)]):
            if context.user_data['captcha'+ str(update.message.from_user.id)]:
                if str(user_code) == str(context.user_data['captcha'+ str(update.message.from_user.id)]): #The user sent the correct captcha code.
                    mensaje=("Bienvenido al grupo "
                            + "<b>" + username + ".</b> "
                            "\n\nSoy Anubis, un Bot creado para ayudar a esta comunidad, puedes encontrar más información sobre mi a través del comando /help."
                            "\n\nRecuerda revisar las /normas del grupo, su incumplimiento resultará en tu expulsión")
                    #Sends the Welcome message.
                    message = await context.bot.send_message(chat_id, mensaje, parse_mode="HTML")
                    #Deletes the correct number sent by the user.
                    await context.bot.delete_message(chat_id=update.message.chat.id,message_id=update.message.message_id)
                    #Deletes the captcha message.
                    await context.bot.delete_message(chat_id=update.message.chat.id,message_id=str(context.user_data['message'+ str(update.message.from_user.id)]))
                    #Deletes the welcome message from the bot.
                    context.job_queue.run_once(callback=your_func_for_delete_message, when=15, data=message.message_id, chat_id=update.message.chat.id)
                    #Wipes the variables we saved on context.
                    del([context.user_data['captcha'+ str(update.message.from_user.id)],context.user_data['userID'+ str(update.message.from_user.id)],context.user_data['intentos'+ str(update.message.from_user.id)],context.user_data['message'+ str(update.message.from_user.id)]])

                else: #The user sent an incorrect captcha number.
                    context.user_data['intentos'+ str(update.message.from_user.id)] = context.user_data['intentos'+ str(update.message.from_user.id)] - 1
                    await context.bot.delete_message(chat_id=update.message.chat.id,message_id=update.message.message_id) 

                    if context.user_data['intentos'+ str(update.message.from_user.id)]  == 0: # Failed 3 times.
                        print('Pa tu puta casa')
                        #Deleting the variables we saved in context and kicking the user.
                        del([context.user_data['captcha'+ str(update.message.from_user.id)],context.user_data['userID'+ str(update.message.from_user.id)],context.user_data['intentos'+ str(update.message.from_user.id)],context.user_data['message'+ str(update.message.from_user.id)]])
                        await context.bot.delete_message(chat_id=update.message.chat.id,message_id=str(context.user_data['message'+ str(update.message.from_user.id)]))
                        await context.bot.ban_chat_member(chat_id, user_id,until_date=5)
                        await context.bot.unban_chat_member(chat_id, user_id)

                    else:
                        text="Código de seguridad incorrecto. Te quedan {} intentos Por favor, inténtalo de nuevo.".format(context.user_data['intentos'+ str(update.message.from_user.id)])
                        message = await context.bot.send_message(chat_id, text) #Sends a message with the amount of tries left.
                        context.job_queue.run_once(callback=your_func_for_delete_message, when=3, data=message.message_id, chat_id=update.message.chat.id) #Deletes the message in 3s.


#Commands

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
   if not await pentesters_community(update): #Calling the verification above.
        mensaje=("📚 Comandos disponibles:"
                "\n/blogs ▫️ Muestra los blogs de usuarios la comunidad."
                "\n/apuntes ▫️ Apuntes de los usuarios de de la comunidad"
                "\n/principiantes ▫️ Recursos para gente nueva en el hacking."
                "\n/vpn ▫️ Dudas relativas a que servicio de VPN usar."
                "\n/normas ▫️ Normas de la comunidad."
                "\n/discord ▫️ Enlace al servidor de Discord.")

        #Sends the message, deletes the user call and waits X seconds to delete the bot response.
        message = await context.bot.send_message(update.message.chat.id, mensaje)
        await context.bot.delete_message(chat_id=update.message.chat.id,message_id=update.message.message_id)
        context.job_queue.run_once(callback=your_func_for_delete_message, when=10, data=message.message_id, chat_id=update.message.chat.id)

#Delete message after X amount of time.
async def your_func_for_delete_message(context: CallbackContext) -> None:
    #We get the message chat and id.
    message_id = context.job.data
    chat_id = context.job.chat_id
    # Deletes the message.
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)


async def blogs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await pentesters_community(update):
        mensaje=("👨‍💻Blogs de los miembros de la comunidad:"
                "\n\nBlog de Slayer: https://slayer0x.github.io/"
                "\nBlog de Juanjo: https://w47son.github.io/"
                "\n\n🧠Si quieres añadir tu página ponte en contacto con Slayer")

        #Sends the message, deletes the user call and waits X secconds to delete the bot response.
        message = await context.bot.send_message(update.message.chat.id,mensaje,disable_web_page_preview=True)
        await context.bot.delete_message(chat_id=update.message.chat.id,message_id=update.message.message_id)
        context.job_queue.run_once(callback=your_func_for_delete_message, when=10, data=message.message_id, chat_id=update.message.chat.id)


async def vpn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await pentesters_community(update):
        mensaje=("☠️ Los servicios de VPN comerciales no garantizan tu seguridad, estás enrutando tu tráfico por servidores de terceros, "
                "la única opción segura es montarte tu propio servidor de VPN.\n \nSi no estas dispuesto a ello, tal vez no te importe tanto "
                "tu privacidad.\nPuedes encontrar tutoriales en internet sobre como crear tu propio servidor de OpenVPN o WireGuard. ☠️")

        #Sends the message, deletes the user call and waits X secconds to delete the bot response.
        message = await context.bot.send_message(update.message.chat.id,mensaje,disable_web_page_preview=True)
        await context.bot.delete_message(chat_id=update.message.chat.id,message_id=update.message.message_id)
        context.job_queue.run_once(callback=your_func_for_delete_message, when=10, data=message.message_id, chat_id=update.message.chat.id)

async def apuntes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await pentesters_community(update):
        mensaje=("\n🔺Si deseas añadir tus apuntes ponte en contacto con Slayer"
                "\nApuntes disponibles (Redteam 🔴 | BlueTeam 🔵 ):"
                "\n\n🔴 Slayer: https://foamy-timbale-1cd.notion.site/READ-TEAM-BY-SLAYER-27747946303f4b4ca2d9bfec8feaf5fe")

        #Sends the message, deletes the user call and waits X secconds to delete the bot response.
        message = await context.bot.send_message(update.message.chat.id,mensaje,disable_web_page_preview=True)
        await context.bot.delete_message(chat_id=update.message.chat.id,message_id=update.message.message_id)
        context.job_queue.run_once(callback=your_func_for_delete_message, when=10, data=message.message_id, chat_id=update.message.chat.id)

async def principiantes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await pentesters_community(update):
        mensaje=("👨‍💻 No existe una única forma de comenzar en el hacking, pero aquí tienes distintos recursos con los que poder empezar:"
                "\n\n Según su enfoque: (📚 = Aprendizaje | 🏴‍☠️ = CTFS):"
                "\n\n🔴 Red Team: "
                "\n\n📚TryHackme https://tryhackme.com/"
                "\n📚TMC Security https://academy.tcm-sec.com/"
                "\n🏴‍☠️Hack The Box https://www.hackthebox.com/"
                "\n🏴‍☠️VulnHub  https://www.vulnhub.com/"
                "\n\n🔵 Blue Team: "
                "\n\n📚TryHackme https://tryhackme.com/"
                "\n📚LetsDefend https://letsdefend.io/"
                "\n🏴‍☠️BlueTeamLabs https://blueteamlabs.online/"
                "\n📚CyberDefenders https://cyberdefenders.org/"
                "\n\n💸Curso gratuito Red/Blue Team:"
                "\n\n📚Brootware https://github.com/brootware/awesome-cyber-security-university"
                "\n\nRecuerda que todo lo anterior tan solo es una sugerencia, existen otras plataformas y contenidos gratuitos.")

        #Sends the message, deletes the user call and waits X secconds to delete the bot response.
        message = await context.bot.send_message(update.message.chat.id,mensaje,disable_web_page_preview=True)
        await context.bot.delete_message(chat_id=update.message.chat.id,message_id=update.message.message_id)
        context.job_queue.run_once(callback=your_func_for_delete_message, when=15, data=message.message_id, chat_id=update.message.chat.id)

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await pentesters_community(update):
        mensaje=("🔥 Grupo de Pentesting 🔥"
                "\n\n▫️ Aprendizaje conjunto"
                "\n▫️ No Scammers"
                "\n▫️ Prohibido Pornografía o Gore"
                "\n▫️ Comparte tus conocimientos con el resto"
                "\n▫️ Pública manuales y apuntes"
                "\n▫️ No vendemos servicios"
                "\n▫️ Si compartes un fichero con malware seras expulsado"
                "\n\n 👽Servidor de Discord disponible en el siguiente enlace"
                "\nhttps://discord.gg/hnHD9KPRS5")

        #Sends the message, deletes the user call and waits X secconds to delete the bot response.
        message = await context.bot.send_message(update.message.chat.id,mensaje,disable_web_page_preview=True)
        await context.bot.delete_message(chat_id=update.message.chat.id,message_id=update.message.message_id)
        context.job_queue.run_once(callback=your_func_for_delete_message, when=10, data=message.message_id, chat_id=update.message.chat.id)

async def discord_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await pentesters_community(update):
        mensaje=("👨‍💻 Pentesters Club 👨‍💻"
                "\n\n👽 Servidor de Discord disponible en el siguiente enlace: 👽"
                "\nhttps://discord.gg/hnHD9KPRS5")

        message = await context.bot.send_message(update.message.chat.id,mensaje,disable_web_page_preview=True)
        await context.bot.delete_message(chat_id=update.message.chat.id,message_id=update.message.message_id)
        context.job_queue.run_once(callback=your_func_for_delete_message, when=10, data=message.message_id, chat_id=update.message.chat.id)

# Handle responses to normal messages, not commands.

def handle_response(text: str) -> str:
    processed: str = text.lower()

    return 'Lo siento, pero anubis solo está disponible en la comunidad de telegram: https://t.me/pentestingESP '

# Handle errors.

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
    

# Main function.
if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    #Commands Handlers.
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('blogs', blogs_command))
    app.add_handler(CommandHandler('apuntes', apuntes_command))
    app.add_handler(CommandHandler('vpn', vpn_command))
    app.add_handler(CommandHandler('principiantes', principiantes_command))
    app.add_handler(CommandHandler('normas', rules_command))
    app.add_handler(CommandHandler('discord', discord_command))
    
    #Handler for new members.
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, send_captcha))

    #Messages Handler.
    app.add_handler(MessageHandler(filters.TEXT, check_captcha))

    #Errors.
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)