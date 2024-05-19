import logging
import re
import paramiko
import os
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import psycopg2


from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TOKEN')
host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

userDB=os.getenv('DB_USER')
passwordDB=os.getenv('DB_PASSWORD')
hostDB=os.getenv('DB_HOST')
portDB=os.getenv('DB_PORT')
database=os.getenv('DB_DATABASE')


# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def connect_db():
    return psycopg2.connect(
        user=userDB,
        password=passwordDB,
        host=hostDB,
        port=portDB,
        dbname=database
    )
def execute_ssh_command(host, port, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=port, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        ssh.close()
        if error:
            return "Error: " + error
        return result if result else "Command executed, but no output returned."
    except Exception as e:
        return f"SSH command execution failed: {str(e)}"

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text
    # Обновленное регулярное выражение для обработки всех указанных форматов
    phone_pattern = re.compile(r'(?:\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}|\b(?:\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}\b')
    phoneNumberList = phone_pattern.findall(user_input)

    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END

    context.user_data['phone_numbers'] = phoneNumberList
    phoneNumbers = '\n'.join([f'{i+1}. {num}' for i, num in enumerate(phoneNumberList)])
    update.message.reply_text(f'Найденные телефонные номера:\n{phoneNumbers}\nХотите сохранить их в базу данных? (да/нет)')
    return 'CONFIRM_SAVE_PHONE'

def save_phone_numbers(update, context):
    if update.message.text.lower() in ['да', 'yes']:
        phone_numbers = context.user_data['phone_numbers']
        save_data(phone_numbers, "phone_numbers")
        update.message.reply_text("Номера телефонов успешно сохранены.")
    else:
        update.message.reply_text("Сохранение отменено.")
    return ConversationHandler.END

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска электронной почты:')

    return 'find_email'

def findEmail (update: Update, context):
    user_input = update.message.text
    email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    emailList = email_pattern.findall(user_input)

    if not emailList:
        update.message.reply_text('Почты не найдены')
        return ConversationHandler.END

    context.user_data['emails'] = emailList
    emails = '\n'.join([f'{i+1}. {email}' for i, email in enumerate(emailList)])
    update.message.reply_text(f'Найденные электронные адреса:\n{emails}\nХотите сохранить их в базу данных? (да/нет)')
    return 'CONFIRM_SAVE_EMAIL'

def save_emails(update, context):
    if update.message.text.lower() in ['да', 'yes']:
        emails = context.user_data['emails']
        save_data(emails, "emails")
        update.message.reply_text("Email-адреса успешно сохранены.")
    else:
        update.message.reply_text("Сохранение отменено.")
    return ConversationHandler.END

def VerifyPassCommand(update: Update, context):
    update.message.reply_text('Введите пароль:')

    return 'verify_password'

def VerifyPass (update: Update, context):
    user_input = update.message.text

    # Регулярное выражение для проверки сложности пароля
    passwordRegex = re.compile(
        r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$'
    )

    if passwordRegex.match(user_input):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    
    return ConversationHandler.END

def get_release(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'cat /etc/os-release')
    update.message.reply_text(f"System Release Information:\n{result}")

def get_uname(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'uname -a')
    update.message.reply_text(f"System uname information:\n{result}")

def get_uptime(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'uptime -p')
    update.message.reply_text(f"System Uptime:\n{result}")

def get_df(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'df -h')
    update.message.reply_text(f"Filesystem Status:\n{result}")

def get_free(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'free -h')
    update.message.reply_text(f"Memory Usage:\n{result}")

def get_mpstat(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'mpstat')
    update.message.reply_text(f"CPU Performance:\n{result}")

def get_w(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'w')
    update.message.reply_text(f"Active Users:\n{result}")

def get_auths(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'last -n 10')
    update.message.reply_text(f"Last 10 Logins:\n{result}")

def get_critical(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'grep CRITICAL /var/log/syslog | tail -n 5')
    update.message.reply_text(f"Last 5 Critical Logs:\n{result}")

def get_ps(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'ps aux | head -n 10')
    update.message.reply_text(f"Current Processes:\n{result}")

def get_ss(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'ss -tulwn')
    update.message.reply_text(f"Network Connections and Ports:\n{result}")

def get_apt_list(update: Update, context):
    update.message.reply_text("Enter a package name to search for, or type 'all' to list all packages.")
    return 'get_apt_list'

def handle_apt_package(update: Update, context):
    package_name = update.message.text
    if package_name.lower() == 'all':
        command = 'dpkg -l | head -n 10'
    else:
        command = f'dpkg -l | grep {package_name} | head -n 10'
    result = execute_ssh_command(host, port, username, password, command)
    update.message.reply_text(f"Package Information:\n{result}")
    return ConversationHandler.END

def get_services(update: Update, context):
    result = execute_ssh_command(host, port, username, password, 'systemctl list-units --type=service --state=running')
    update.message.reply_text(f"Active Services:\n{result}")

def get_repl_logs(update: Update, context):
    query = update.message.text.split()
    if len(query) < 2:
        update.message.reply_text("Please specify a filter keyword from 'start', 'stop', 'ready'. For example: /get_repl_logs start")
        return

    filter_keyword = query[1].lower()
    # Настройка ключевых слов для grep в зависимости от запрашиваемой информации
    if filter_keyword == 'start':
        grep_keyword = "START_REPLICATION"  # Пример ключевого слова для запуска
    elif filter_keyword == 'stop':
        grep_keyword = "stop"  # Пример ключевого слова для остановки
    elif filter_keyword == 'ready':
        grep_keyword = "database system is ready to accept connections"  # Пример ключевого слова для готовност
    else:
        update.message.reply_text("Invalid filter keyword. Use 'start', 'stop', or 'ready'.")
        return

    command = f"docker logs devops-db-1 | grep '{grep_keyword}' | head -n 10"
    result = execute_ssh_command(host, port, username, password, command)
    if result:
        update.message.reply_text(f"PostgreSQL Replication Logs for '{filter_keyword}':\n{result}")
    else:
        update.message.reply_text("No relevant logs found or access denied.")

def get_emails(update: Update, context):
    try:
        connection = connect_db()
        cur = connection.cursor()
        cur.execute("SELECT email FROM email_table;")
        emails = cur.fetchall()
        if emails:
            email_text = "\n".join(email[0] for email in emails)
            update.message.reply_text(f"Emails:\n{email_text}")
        else:
            update.message.reply_text("No emails found.")
        cur.close()
        connection.close()
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

def get_phone_numbers(update: Update, context):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT phone_number FROM phone_table;")
        numbers = cur.fetchall()
        if numbers:
            phone_text = "\n".join(number[0] for number in numbers)
            update.message.reply_text(f"Phone Numbers:\n{phone_text}")
        else:
         update.message.reply_text("No phone numbers found.")
        cur.close()
        conn.close()
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

def save_data(items, table_name):
    conn = connect_db()
    cur = conn.cursor()
    if table_name == "emails":
        insert_query = "INSERT INTO email_table (email) VALUES (%s) ON CONFLICT DO NOTHING;"
    else:
        insert_query = "INSERT INTO phone_table (phone_number) VALUES (%s) ON CONFLICT DO NOTHING;"

    for item in items:
        cur.execute(insert_query, (item,))
    conn.commit()
    cur.close()
    conn.close()

def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerEmailAndNumber = ConversationHandler(
        entry_points=[
            CommandHandler('find_email', findEmailCommand),
            CommandHandler('find_phone_number', findPhoneNumbersCommand)
        ],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'CONFIRM_SAVE_EMAIL': [MessageHandler(Filters.text & ~Filters.command, save_emails)],
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'CONFIRM_SAVE_PHONE': [MessageHandler(Filters.text & ~Filters.command, save_phone_numbers)]
        },
        fallbacks=[]
    )
    convHandlerVerifyPass = ConversationHandler(
        entry_points=[CommandHandler('verify_password', VerifyPassCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, VerifyPass)],
        },
        fallbacks=[]
    )

    convHandlerAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, handle_apt_package)],
        },
        fallbacks=[]
    )

	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerEmailAndNumber)	
    dp.add_handler(convHandlerVerifyPass)
    dp.add_handler(CommandHandler('get_release', get_release))
    dp.add_handler(CommandHandler('get_uname', get_uname))
    dp.add_handler(CommandHandler('get_uptime', get_uptime))
    dp.add_handler(CommandHandler('get_df', get_df))
    dp.add_handler(CommandHandler('get_free', get_free))
    dp.add_handler(CommandHandler('get_mpstat', get_mpstat))
    dp.add_handler(CommandHandler('get_w', get_w))
    dp.add_handler(CommandHandler('get_auths', get_auths))
    dp.add_handler(CommandHandler('get_critical', get_critical))
    dp.add_handler(convHandlerAptList)
    dp.add_handler(CommandHandler('get_ps', get_ps))
    dp.add_handler(CommandHandler('get_ss', get_ss))
    dp.add_handler(CommandHandler('get_services', get_services))
    dp.add_handler(CommandHandler('get_repl_logs', get_repl_logs))
    dp.add_handler(CommandHandler('get_emails', get_emails))
    dp.add_handler(CommandHandler('get_phone_numbers', get_phone_numbers))
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
