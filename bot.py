# -*- coding: utf-8 -*-
import telebot
from telebot import types
import random
import string
import time
from collections import defaultdict
import os
import sqlite3
from functools import wraps
import re
import threading

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8014595426:AAEI79qXWfg17xkagkOc2_e2tXHDIoomjek"
MAIN_OWNER = 8216255332
OWNERS = [8216255332]
LOG_CHANNEL_ID = -1003007771264
GROUP_ID = -1003031831608

BOT_NAME = "Elf Guard"
MIN_DEAL_AMOUNTS = {
    'TON': 2.0, 'USDT': 5.0, 'RUB': 200.0, 'STARS': 250.0,
    'KGS': 38500.0, 'IDR': 1250.0, 'UAH': 100.0, 'UZS': 30000.0,
    'BYN': 8.0, 'BTC': 0.00002068
}

AVAILABLE_CURRENCIES = ['TON', 'USDT', 'RUB', 'STARS', 'KGS', 'IDR', 'UAH', 'UZS', 'BYN', 'BTC']

# ========== ПЕРЕВОДЫ ==========
TRANSLATIONS = {
    'ru': {
        'welcome': "💎 Добро пожаловать в {}\n\nВыберите действие:",
        'create_deal_seller': "📝 Продать",
        'create_deal_buyer': "🛒 Купить",
        'balance': "💰 Баланс",
        'details': "💳 Реквизиты",
        'my_stats': "📈 Моя статистика",
        'back': "🔙 Назад",
        'skip': "⏭️ Пропустить",
        'insufficient_funds': "❌ Недостаточно средств!\nВаш баланс: {} {}\nТребуется: {} {}",
        'deal_not_found': "❌ Сделка не найдена!",
        'wrong_pin': "❌ Неверный пин-код!",
        'cannot_join_self': "❌ Нельзя присоединиться к своей сделке!",
        'deal_already_taken': "❌ Сделка уже занята!",
        'no_payment_details': "❌ Сначала добавьте реквизиты для получения оплаты!",
        'no_pin': "🔐 У вас нет пин-кода. Создайте его через /start",
        'enter_pin': "🔐 Введите ваш пин-код для подтверждения создания сделки:",
        'pin_setup': "🔐 Для безопасности создайте пин-код для сделок.\nОн будет запрашиваться при каждой новой сделке.\n\nОтправьте цифровой пин-код (4-6 цифр):",
        'pin_saved': "✅ Пин-код сохранён! Теперь он будет запрашиваться при создании сделок.",
        'pin_format_error': "❌ Пин-код должен содержать 4-6 цифр. Попробуйте снова:",
        'select_currency': "💰 Выберите валюту сделки:",
        'enter_amount': "📊 Введите сумму в {}:",
        'enter_amount_buyer': "📊 Введите сумму в {} (которую хотите купить):",
        'min_amount_error': "❌ Минимальная сумма: {} {}\nВведите снова:",
        'invalid_number': "❌ Введите корректное число!",
        'enter_nft_link': "🔗 Отправьте ссылку на NFT (пример: https://t.me/nft/PlushPepe-1040):",
        'enter_nft_link_buyer': "🔗 Отправьте ссылку на NFT (который хотите купить):",
        'invalid_nft_link': "❌ Неверный формат ссылки на NFT!\nСсылка должна быть вида: https://t.me/nft/Название-число",
        'retry_nft': "🔄 Попробовать снова",
        'deal_created': "✅ Сделка #{} создана!\nРоль: {}\nСумма: {} {}\nNFT: {}\n\n🔗 Ссылка для {}:\n{}",
        'role_seller': "Продавец",
        'role_buyer': "Покупатель (ищу продавца)",
        'link_for_buyer': "покупателя",
        'link_for_seller': "продавца",
        'creator_stats': "📊 <b>Статистика создателя сделки:</b>\n✅ Успешных: {}\n❌ Отзывов: {}\n⭐ Рейтинг: {}%",
        'your_stats': "📊 <b>Ваша статистика:</b>\n✅ Успешных: {}\n❌ Отзывов: {}\n⭐ Рейтинг: {}%",
        'nft_link_label': "🖼️ <b>NFT:</b>\n{}",
        'confirm_deal': "✅ Подтверждаю сделку и оплачиваю",
        'cancel_deal': "❌ Отмена",
        'deal_cancelled': "❌ Сделка отменена.",
        'buyer_confirmed': "✅ Вы произвели оплату по сделке,метод:СБП Перевод #{}!\n\nСредства списаны с вашего баланса.\nОжидайте, продавец отправит вам NFT и предоставит хэш транзакции.",
        'seller_joined': "✅ Вы присоединились к сделке #{}!\n\nОжидайте подтверждения оплаты от покупателя.",
        'buyer_joined_notification': "🔔 <b>Покупатель перешёл по ссылке на сделку #{}</b>\n\nПокупатель: @{}\n\n📊 <b>Статистика покупателя:</b>\n✅ Успешных: {}\n❌ Отзывов: {}\n⭐ Рейтинг: {}%\n\n🖼️ <b>NFT ссылка:</b> {}\n\n⏳ Ожидайте, пока покупатель подтвердит сделку и оплатит.",
        'buyer_paid_notification': "⚡ <b>Покупатель произвел оплату по сделке #{}</b>\n\nПокупатель: @{}\nСумма: {} {}\n🖼️ <b>NFT ссылка:</b> {}\n\n📊 <b>Статистика покупателя:</b>\n✅ Успешных: {}\n❌ Отзывов: {}\n\n⚠️ <b>Важно!</b>\nПереведите NFT покупателю: @{}\n\n⛓После отправки отправьте ID операции в этот чат.",
        'seller_joined_deal': "✅ <b>Продавец присоединился к вашей сделке #{}!</b>\n\nПродавец: @{}\nСумма: {} {}\nNFT: {}\n\n📊 <b>Статистика продавца:</b>\n✅ Успешных: {}\n❌ Отзывов: {}\n\n⚠️ Теперь отправьте продавцу оплату в размере {} {} и предоставьте хэш транзакции.",
        'hash_checking': "🔄 <b>Проеврка ID транзакции...</b>\n\nПожалуйста, подождите 3-5 секунд.",
        'hash_valid': "✅ ID транзакции проверен и принят!\n\nХэш: <code>{}</code>\n\nОжидайте подтверждения от покупателя.",
        'hash_invalid': "❌ ID транзакции невалидный!\n\nПроверьте правильность хэша и отправьте снова.\nХэш: <code>{}</code>\n\n⚠️ Средства покупателя заблокированы до предоставления корректного хэша.",
        'send_hash_again': "🔗 Пожалуйста, отправьте корректный ХЭШ транзакции перевода покупателю:",
        'asset_sent': "📦 <b>Продавец отправил актив по сделке #{}!</b>\n\nХэш транзакции:\n<code>{}</code>\n\nNFT: {}\n\n✅ Подтвердите получение актива, чтобы продавец получил оплату.",
        'confirm_receipt': "✅ Подтвердить получение",
        'complaint': "❌ Жалоба (актив не получен)",
        'receipt_confirmed': "✅ Спасибо за подтверждение!\n\nСделка #{} успешно завершена.\nСредства переведены продавцу.",
        'seller_paid': "✅ Покупатель подтвердил получение актива по сделке #{}!\n\nСумма {} {} зачислена на ваш баланс.",
        'complaint_sent': "⚠️ Жалоба отправлена администратору!",
        'payment_details': "📩 <b>Ваши реквизиты</b>\n\n💎 TON: {}\n💳 Карта: {}\n\nРеквизиты нужны для получения выплат",
        'add_ton': "💎 Добавить TON",
        'add_card': "💳 Добавить карту",
        'enter_ton': "💎 Введите адрес TON кошелька:",
        'enter_card': "💳 Введите номер карты:",
        'ton_saved': "✅ TON кошелек сохранен",
        'card_saved': "✅ Карта сохранена",
        'back_to_menu': "Вы можете вернуться в меню:",
        'balance_header': "💰 <b>Ваш баланс</b>\n\n",
        'no_funds': "У вас пока нет средств",
        'stats_header': "⭐ <b>Ваша статистика</b>\n\n",
        'successful': "✅ Успешных сделок: {}",
        'failed': "❌ Провальных/отзывов: {}",
        'rating': "📊 Рейтинг: {}%",
        'select_language': "🌐 Выберите язык / Select your language / 选择你的语言:",
        'language_set': "✅ Язык установлен: Русский!",
        'use_menu_buttons': "Используйте кнопки меню.",
        'you_banned': "🚫 Вы забанены!",
        'admin_only': "❌ Только для главного админа!",
    },
    'en': {
        'welcome': "💎 Welcome to {}\n\nChoose an action:",
        'create_deal_seller': "📝 Create deal (seller)",
        'create_deal_buyer': "🛒 Create deal (buyer)",
        'balance': "💰 Balance",
        'details': "📩 Payment details",
        'my_stats': "⭐ My stats",
        'back': "🔙 Back",
        'skip': "⏭️ Skip (can add later)",
        'insufficient_funds': "❌ Insufficient funds!\nYour balance: {} {}\nRequired: {} {}",
        'deal_not_found': "❌ Deal not found!",
        'wrong_pin': "❌ Wrong PIN code!",
        'cannot_join_self': "❌ Cannot join your own deal!",
        'deal_already_taken': "❌ Deal already taken!",
        'no_payment_details': "❌ First add payment details to receive payment!",
        'no_pin': "🔐 You don't have a PIN. Create it with /start",
        'enter_pin': "🔐 Enter your PIN to confirm deal creation:",
        'pin_setup': "🔐 For security, create a PIN code for deals.\nIt will be requested for each new deal.\n\nSend a numeric PIN code (4-6 digits):",
        'pin_saved': "✅ PIN saved! It will be requested when creating deals.",
        'pin_format_error': "❌ PIN must be 4-6 digits. Try again:",
        'select_currency': "💰 Select deal currency:",
        'enter_amount': "📊 Enter amount in {}:",
        'enter_amount_buyer': "📊 Enter amount in {} (you want to buy):",
        'min_amount_error': "❌ Minimum amount: {} {}\nEnter again:",
        'invalid_number': "❌ Enter a valid number!",
        'enter_nft_link': "🔗 Send NFT link (example: https://t.me/nft/PlushPepe-1040):",
        'enter_nft_link_buyer': "🔗 Send NFT link (you want to buy):",
        'invalid_nft_link': "❌ Invalid NFT link format!\nLink must be like: https://t.me/nft/Name-number",
        'retry_nft': "🔄 Try again",
        'deal_created': "✅ Deal #{} created!\nRole: {}\nAmount: {} {}\nNFT: {}\n\n🔗 Link for {}:\n{}",
        'role_seller': "Seller",
        'role_buyer': "Buyer (looking for seller)",
        'link_for_buyer': "buyer",
        'link_for_seller': "seller",
        'creator_stats': "📊 <b>Creator's stats:</b>\n✅ Successful: {}\n❌ Failed: {}\n⭐ Rating: {}%",
        'your_stats': "📊 <b>Your stats:</b>\n✅ Successful: {}\n❌ Failed: {}\n⭐ Rating: {}%",
        'nft_link_label': "🖼️ <b>NFT link:</b>\n{}",
        'confirm_deal': "✅ Confirm deal and pay",
        'cancel_deal': "❌ Cancel",
        'deal_cancelled': "❌ Deal cancelled.",
        'buyer_confirmed': "✅ You confirmed deal #{}!\n\nFunds deducted from your balance.\nWait for the seller to send the NFT and provide transaction hash.",
        'seller_joined': "✅ You joined deal #{}!\n\nWait for buyer to confirm and pay.",
        'buyer_joined_notification': "🔔 <b>Buyer opened deal #{}</b>\n\nBuyer: @{}\n\n📊 <b>Buyer's stats:</b>\n✅ Successful: {}\n❌ Failed: {}\n⭐ Rating: {}%\n\n🖼️ <b>NFT link:</b> {}\n\n⏳ Waiting for buyer to confirm and pay.",
        'buyer_paid_notification': "✅ <b>Buyer confirmed deal #{} and PAID!</b>\n\nBuyer: @{}\nAmount: {} {}\n🖼️ <b>NFT link:</b> {}\n\n📊 <b>Buyer's stats:</b>\n✅ Successful: {}\n❌ Failed: {}\n\n⚠️ <b>IMPORTANT!</b>\nSend the asset (NFT/gift) to BUYER: @{}\n\nAfter sending, send the TRANSACTION HASH in this chat.",
        'seller_joined_deal': "✅ <b>Seller joined your deal #{}!</b>\n\nSeller: @{}\nAmount: {} {}\nNFT: {}\n\n📊 <b>Seller's stats:</b>\n✅ Successful: {}\n❌ Failed: {}\n\n⚠️ Now send the payment of {} {} to the seller and provide the transaction hash.",
        'hash_checking': "🔄 <b>CHECKING TRANSACTION HASH...</b>\n\nPlease wait 3-5 seconds.",
        'hash_valid': "✅ TRANSACTION HASH VERIFIED AND ACCEPTED!\n\nHash: <code>{}</code>\n\nWaiting for buyer confirmation.",
        'hash_invalid': "❌ TRANSACTION HASH IS INVALID!\n\nCheck the hash and send again.\nHash: <code>{}</code>\n\n⚠️ Buyer's funds are locked until a valid hash is provided.",
        'send_hash_again': "🔗 Please send a valid transaction hash for the transfer to the buyer:",
        'asset_sent': "📦 <b>Seller sent the asset for deal #{}!</b>\n\nTransaction hash:\n<code>{}</code>\n\nNFT: {}\n\n✅ Confirm receipt so the seller gets paid.",
        'confirm_receipt': "✅ Confirm receipt",
        'complaint': "❌ Complaint (asset not received)",
        'receipt_confirmed': "✅ Thank you for confirming!\n\nDeal #{} completed successfully.\nFunds transferred to seller.",
        'seller_paid': "✅ Buyer confirmed receipt of asset for deal #{}!\n\nAmount {} {} added to your balance.",
        'complaint_sent': "⚠️ Complaint sent to admin!",
        'payment_details': "📩 <b>Your payment details</b>\n\n💎 TON: {}\n💳 Card: {}\n\nDetails needed to receive payments",
        'add_ton': "💎 Add TON",
        'add_card': "💳 Add card",
        'enter_ton': "💎 Enter TON wallet address:",
        'enter_card': "💳 Enter card number:",
        'ton_saved': "✅ TON wallet saved",
        'card_saved': "✅ Card saved",
        'back_to_menu': "You can return to menu:",
        'balance_header': "💰 <b>Your balance</b>\n\n",
        'no_funds': "No funds yet",
        'stats_header': "⭐ <b>Your stats</b>\n\n",
        'successful': "✅ Successful deals: {}",
        'failed': "❌ Failed deals: {}",
        'rating': "📊 Rating: {}%",
        'select_language': "🌐 Select your language / Выберите язык / 选择你的语言:",
        'language_set': "✅ Language set: English!",
        'use_menu_buttons': "Use the menu buttons.",
        'you_banned': "🚫 You are banned!",
        'admin_only': "❌ Only for main admin!",
    },
    'zh': {
        'welcome': "💎 欢迎来到 {}\n\n请选择操作:",
        'create_deal_seller': "📝 创建交易 (卖家)",
        'create_deal_buyer': "🛒 创建交易 (买家)",
        'balance': "💰 余额",
        'details': "📩 支付信息",
        'my_stats': "⭐ 我的统计",
        'back': "🔙 返回",
        'skip': "⏭️ 跳过 (可以稍后添加)",
        'insufficient_funds': "❌ 余额不足！\n您的余额：{} {}\n需要：{} {}",
        'deal_not_found': "❌ 交易未找到！",
        'wrong_pin': "❌ 错误的PIN码！",
        'cannot_join_self': "❌ 不能加入自己的交易！",
        'deal_already_taken': "❌ 交易已被占用！",
        'no_payment_details': "❌ 请先添加支付信息以接收付款！",
        'no_pin': "🔐 您没有PIN码。请通过 /start 创建",
        'enter_pin': "🔐 请输入您的PIN码以确认创建交易：",
        'pin_setup': "🔐 为了安全，请为交易创建PIN码。\n每次创建新交易时都会要求输入。\n\n请发送4-6位数字的PIN码：",
        'pin_saved': "✅ PIN码已保存！创建交易时会要求输入。",
        'pin_format_error': "❌ PIN码必须为4-6位数字。请重试：",
        'select_currency': "💰 选择交易货币：",
        'enter_amount': "📊 输入 {} 金额：",
        'enter_amount_buyer': "📊 输入 {} 金额 (您想购买的金额)：",
        'min_amount_error': "❌ 最小金额：{} {}\n请重新输入：",
        'invalid_number': "❌ 请输入有效数字！",
        'enter_nft_link': "🔗 发送NFT链接 (例如：https://t.me/nft/PlushPepe-1040)：",
        'enter_nft_link_buyer': "🔗 发送NFT链接 (您想购买的NFT)：",
        'invalid_nft_link': "❌ NFT链接格式无效！\n链接格式应为：https://t.me/nft/名称-数字",
        'retry_nft': "🔄 重试",
        'deal_created': "✅ 交易 #{} 已创建！\n角色：{}\n金额：{} {}\nNFT：{}\n\n🔗 {} 的链接：\n{}",
        'role_seller': "卖家",
        'role_buyer': "买家 (寻找卖家)",
        'link_for_buyer': "买家",
        'link_for_seller': "卖家",
        'creator_stats': "📊 <b>创建者统计：</b>\n✅ 成功：{}\n❌ 失败：{}\n⭐ 评分：{}%",
        'your_stats': "📊 <b>您的统计：</b>\n✅ 成功：{}\n❌ 失败：{}\n⭐ 评分：{}%",
        'nft_link_label': "🖼️ <b>NFT链接：</b>\n{}",
        'confirm_deal': "✅ 确认交易并支付",
        'cancel_deal': "❌ 取消",
        'deal_cancelled': "❌ 交易已取消。",
        'buyer_confirmed': "✅ 您已确认交易 #{}！\n\n资金已从您的余额中扣除。\n请等待卖家发送NFT并提供交易哈希。",
        'seller_joined': "✅ 您已加入交易 #{}！\n\n等待买家确认并付款。",
        'buyer_joined_notification': "🔔 <b>买家打开了交易 #{}</b>\n\n买家：@{}\n\n📊 <b>买家统计：</b>\n✅ 成功：{}\n❌ 失败：{}\n⭐ 评分：{}%\n\n🖼️ <b>NFT链接：</b>{}\n\n⏳ 等待买家确认并付款。",
        'buyer_paid_notification': "✅ <b>买家已确认交易 #{} 并已付款！</b>\n\n买家：@{}\n金额：{} {}\n🖼️ <b>NFT链接：</b>{}\n\n📊 <b>买家统计：</b>\n✅ 成功：{}\n❌ 失败：{}\n\n⚠️ <b>重要！</b>\n请将资产(NFT/礼物)发送给买家：@{}\n\n发送后，请在此聊天中发送交易哈希。",
        'seller_joined_deal': "✅ <b>卖家已加入您的交易 #{}！</b>\n\n卖家：@{}\n金额：{} {}\nNFT：{}\n\n📊 <b>卖家统计：</b>\n✅ 成功：{}\n❌ 失败：{}\n\n⚠️ 请向卖家支付 {} {} 并提供交易哈希。",
        'hash_checking': "🔄 <b>正在验证交易哈希...</b>\n\n请等待3-5秒。",
        'hash_valid': "✅ 交易哈希已验证并接受！\n\n哈希：<code>{}</code>\n\n等待买家确认。",
        'hash_invalid': "❌ 交易哈希无效！\n\n请检查哈希并重新发送。\n哈希：<code>{}</code>\n\n⚠️ 买家的资金已被锁定，直到提供有效哈希。",
        'send_hash_again': "🔗 请向买家发送有效的交易哈希：",
        'asset_sent': "📦 <b>卖家已发送交易 #{} 的资产！</b>\n\n交易哈希：\n<code>{}</code>\n\nNFT：{}\n\n✅ 请确认收货，以便卖家收到付款。",
        'confirm_receipt': "✅ 确认收货",
        'complaint': "❌ 投诉 (未收到资产)",
        'receipt_confirmed': "✅ 感谢确认！\n\n交易 #{} 已成功完成。\n资金已转给卖家。",
        'seller_paid': "✅ 买家已确认收到交易 #{} 的资产！\n\n金额 {} {} 已添加到您的余额。",
        'complaint_sent': "⚠️ 投诉已发送给管理员！",
        'payment_details': "📩 <b>您的支付信息</b>\n\n💎 TON：{}\n💳 银行卡：{}\n\n需要这些信息来接收付款",
        'add_ton': "💎 添加TON",
        'add_card': "💳 添加银行卡",
        'enter_ton': "💎 请输入TON钱包地址：",
        'enter_card': "💳 请输入银行卡号：",
        'ton_saved': "✅ TON钱包已保存",
        'card_saved': "✅ 银行卡已保存",
        'back_to_menu': "您可以返回菜单：",
        'balance_header': "💰 <b>您的余额</b>\n\n",
        'no_funds': "暂无资金",
        'stats_header': "⭐ <b>您的统计</b>\n\n",
        'successful': "✅ 成功交易：{}",
        'failed': "❌ 失败交易：{}",
        'rating': "📊 评分：{}%",
        'select_language': "🌐 选择你的语言 / Select your language / Выберите язык:",
        'language_set': "✅ 语言已设置：中文！",
        'use_menu_buttons': "请使用菜单按钮。",
        'you_banned': "🚫 您已被封禁！",
        'admin_only': "❌ 仅限主管理员！",
    }
}

# ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
bot = telebot.TeleBot(BOT_TOKEN)
bot.timeout = 30

# ========== БАЗА ДАННЫХ ==========
def get_db():
    conn = sqlite3.connect('bot.db', timeout=20)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    return conn

def init_db():
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS orders (
                deal_code TEXT PRIMARY KEY, 
                creator_id TEXT, 
                role TEXT, 
                amount REAL,
                currency TEXT, 
                description TEXT, 
                status TEXT, 
                counterparty_id TEXT,
                payment_method TEXT, 
                payment_status TEXT DEFAULT 'no_paid', 
                deal_type TEXT DEFAULT 'gift',
                nft_link TEXT,
                transaction_hash TEXT,
                pin_code TEXT
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS user_data (
                user_id TEXT PRIMARY KEY, 
                successful_deals INTEGER DEFAULT 0,
                failed_deals INTEGER DEFAULT 0,
                ton_wallet TEXT, 
                card TEXT,
                user_pin TEXT,
                language TEXT DEFAULT 'ru'
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS user_balances (
                user_id TEXT, 
                currency TEXT, 
                amount REAL DEFAULT 0,
                PRIMARY KEY (user_id, currency)
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS banned_users (
                user_id TEXT PRIMARY KEY
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS user_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id TEXT,
                from_id TEXT,
                review_type TEXT,
                comment TEXT,
                deal_code TEXT,
                timestamp REAL
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS valid_hashes (
                hash_value TEXT PRIMARY KEY,
                is_valid INTEGER DEFAULT 1
            )''')
            
            conn.commit()
    except Exception as e:
        print(f"DB init error: {e}")

init_db()

# ========== ЗАГРУЗКА ДАННЫХ ==========
def load_banned_users():
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('SELECT user_id FROM banned_users')
            return [int(row[0]) for row in c.fetchall() if row[0].isdigit()]
    except:
        return []

def load_user_balances():
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('SELECT user_id, currency, amount FROM user_balances')
            balances = defaultdict(lambda: defaultdict(float))
            for user_id, currency, amount in c.fetchall():
                balances[user_id][currency] = amount
            return balances
    except:
        return defaultdict(lambda: defaultdict(float))

def load_user_data():
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('SELECT user_id, successful_deals, failed_deals, ton_wallet, card, user_pin, language FROM user_data')
            data = {}
            for row in c.fetchall():
                user_id, deals, failed, wallet, card, pin, lang = row
                data[user_id] = {
                    'successful_deals': deals or 0,
                    'failed_deals': failed or 0,
                    'ton_wallet': wallet,
                    'card': card,
                    'user_pin': pin,
                    'language': lang or 'ru'
                }
            return data
    except:
        return {}

def load_orders():
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM orders')
            orders = {}
            for row in c.fetchall():
                if len(row) >= 13:
                    (deal_code, creator_id, role, amount, currency, desc, status, 
                     counterparty, payment_method, payment_status, deal_type, nft_link, transaction_hash) = row[:13]
                    pin_code = row[13] if len(row) > 13 else None
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
                        'deal_type': deal_type,
                        'nft_link': nft_link,
                        'transaction_hash': transaction_hash,
                        'pin_code': pin_code
                    }
            return orders
    except:
        return {}

def load_users():
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('SELECT user_id FROM users')
            return set(int(row[0]) for row in c.fetchall() if row[0].isdigit())
    except:
        return set()

def load_valid_hashes():
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('SELECT hash_value FROM valid_hashes WHERE is_valid = 1')
            return set(row[0] for row in c.fetchall())
    except:
        return set()

def get_user_language(user_id):
    uid = str(user_id)
    if uid in user_data:
        return user_data[uid].get('language', 'ru')
    return 'ru'

def get_text(user_id, key, *args):
    lang = get_user_language(user_id)
    text = TRANSLATIONS.get(lang, TRANSLATIONS['ru']).get(key, key)
    if args:
        return text.format(*args)
    return text

# ========== СОХРАНЕНИЕ ДАННЫХ ==========
def save_orders(orders):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM orders')
            for code, deal in orders.items():
                c.execute('''INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                          (code, str(deal.get('creator_id')), deal.get('role'), deal.get('amount'),
                           deal.get('currency'), deal.get('description'), deal.get('status'),
                           str(deal.get('counterparty_id')), deal.get('payment_method', 'ton'),
                           deal.get('payment_status', 'no_paid'), deal.get('deal_type', 'gift'),
                           deal.get('nft_link'), deal.get('transaction_hash'), deal.get('pin_code')))
            conn.commit()
    except Exception as e:
        print(f"Save orders error: {e}")

def save_user_data(data):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM user_data')
            for uid, d in data.items():
                c.execute('INSERT INTO user_data VALUES (?,?,?,?,?,?,?)',
                          (uid, d.get('successful_deals', 0), d.get('failed_deals', 0),
                           d.get('ton_wallet'), d.get('card'), d.get('user_pin'), d.get('language', 'ru')))
            conn.commit()
    except Exception as e:
        print(f"Save user data error: {e}")

def save_user_balances(balances):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM user_balances')
            for uid, b in balances.items():
                for curr, amt in b.items():
                    if amt > 0:
                        c.execute('INSERT INTO user_balances VALUES (?,?,?)', (uid, curr, amt))
            conn.commit()
    except Exception as e:
        print(f"Save balances error: {e}")

def save_users(users):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM users')
            for uid in users:
                c.execute('INSERT INTO users VALUES (?)', (str(uid),))
            conn.commit()
    except Exception as e:
        print(f"Save users error: {e}")

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
BANNED_USERS = load_banned_users()
user_balances = load_user_balances()
user_data = load_user_data()
orders = load_orders()
users = load_users()
user_states = {}
message_ids = {}
temp_deal_data = {}
VALID_HASHES = load_valid_hashes()

def init_demo_hashes():
    demo_hashes = [
        "0x742d35Cc6634C0532925a3b844Bc9e7595f0beb5",
        "0x1234567890abcdef1234567890abcdef12345678",
        "0xabcdef1234567890abcdef1234567890abcdef12"
    ]
    with get_db() as conn:
        c = conn.cursor()
        for h in demo_hashes:
            c.execute('INSERT OR IGNORE INTO valid_hashes VALUES (?, 1)', (h,))
        conn.commit()

init_demo_hashes()
VALID_HASHES = load_valid_hashes()

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

def has_pin_code(user_id):
    uid = str(user_id)
    if uid not in user_data:
        return False
    return bool(user_data[uid].get('user_pin'))

def validate_nft_link(link):
    pattern = r'https?://t\.me/nft/[\w\-]+(?:-\d+)?'
    return re.match(pattern, link) is not None

def validate_transaction_hash(tx_hash):
    return tx_hash in VALID_HASHES

def calculate_rating(success, failed):
    total = success + failed
    if total == 0:
        return 100
    return round((success / total) * 100, 1)

def restrict_banned_users(handler):
    @wraps(handler)
    def wrapped(message):
        if message.from_user.id in BANNED_USERS:
            bot.send_message(message.chat.id, get_text(message.from_user.id, 'you_banned'))
            return
        return handler(message)
    return wrapped

def main_admin_only(handler):
    @wraps(handler)
    def wrapped(message):
        if message.from_user.id != MAIN_OWNER:
            bot.send_message(message.chat.id, get_text(message.from_user.id, 'admin_only'))
            return
        return handler(message)
    return wrapped

def safe_send_or_edit(chat_id, text, reply_markup=None):
    if chat_id in message_ids:
        try:
            bot.delete_message(chat_id, message_ids[chat_id])
        except:
            pass
    
    msg = bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=reply_markup)
    message_ids[chat_id] = msg.message_id
    return msg

# ========== ВЫБОР ЯЗЫКА ==========
def send_language_selection(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
        types.InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
        types.InlineKeyboardButton("🇨🇳 中文", callback_data='lang_zh')
    )
    bot.send_message(chat_id, TRANSLATIONS['ru']['select_language'], reply_markup=markup)

def process_language_selection(call):
    lang = call.data.split('_')[1]
    user_id = str(call.from_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {
            'successful_deals': 0,
            'failed_deals': 0,
            'ton_wallet': None,
            'card': None,
            'user_pin': None,
            'language': lang
        }
    else:
        user_data[user_id]['language'] = lang
    save_user_data(user_data)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=get_text(user_id, 'language_set')
    )
    
    if not has_pin_code(call.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(get_text(user_id, 'skip'), callback_data='skip_pin'))
        bot.send_message(call.message.chat.id, 
            get_text(user_id, 'pin_setup'),
            reply_markup=markup)
        user_states[call.message.chat.id] = 'waiting_pin'
    else:
        send_main_menu(call.message.chat.id, call.from_user.id)
    
    bot.answer_callback_query(call.id)

# ========== МЕНЮ ==========
def send_main_menu(chat_id, user_id):
    try:
        t = get_text
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(t(user_id, 'create_deal_seller'), callback_data='create_deal_seller'),
            types.InlineKeyboardButton(t(user_id, 'create_deal_buyer'), callback_data='create_deal_buyer'),
            types.InlineKeyboardButton(t(user_id, 'balance'), callback_data='check_balance'),
            types.InlineKeyboardButton(t(user_id, 'details'), callback_data='manage_details'),
            types.InlineKeyboardButton(t(user_id, 'my_stats'), callback_data='my_stats')
        )
        
        text = t(user_id, 'welcome').format(BOT_NAME)
        
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

def show_my_stats(call):
    user_id = str(call.from_user.id)
    stats = user_data.get(user_id, {'successful_deals': 0, 'failed_deals': 0})
    t = get_text
    
    rating = calculate_rating(stats.get('successful_deals', 0), stats.get('failed_deals', 0))
    
    text = t(user_id, 'stats_header')
    text += t(user_id, 'successful').format(stats.get('successful_deals', 0)) + "\n"
    text += t(user_id, 'failed').format(stats.get('failed_deals', 0)) + "\n\n"
    text += t(user_id, 'rating').format(rating)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t(user_id, 'back'), callback_data='back_to_menu'))
    
    try:
        bot.edit_message_caption(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                caption=text, parse_mode='HTML',
                                reply_markup=markup)
    except:
        safe_send_or_edit(call.message.chat.id, text, markup)
    
    bot.answer_callback_query(call.id)

# ========== КОМАНДЫ ДЛЯ НАКРУТКИ СТАТИСТИКИ ==========
@bot.message_handler(commands=['add_success'])
@main_admin_only
def add_success_deal(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "Use: /add_success user_id [count]")
            return
        
        target_id = str(args[1])
        count = int(args[2]) if len(args) > 2 else 1
        
        if target_id not in user_data:
            user_data[target_id] = {'successful_deals': 0, 'failed_deals': 0, 'ton_wallet': None, 'card': None, 'user_pin': None, 'language': 'ru'}
        
        user_data[target_id]['successful_deals'] = user_data[target_id].get('successful_deals', 0) + count
        save_user_data(user_data)
        
        bot.send_message(message.chat.id, f"✅ User {target_id} +{count} successful deals")
        log_to_channel(f"📈 Admin added +{count} successful deals to {target_id}")
        
        try:
            bot.send_message(int(target_id), get_text(target_id, 'successful').format(count))
        except:
            pass
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['add_failed'])
@main_admin_only
def add_failed_deal(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "Use: /add_failed user_id [count]")
            return
        
        target_id = str(args[1])
        count = int(args[2]) if len(args) > 2 else 1
        
        if target_id not in user_data:
            user_data[target_id] = {'successful_deals': 0, 'failed_deals': 0, 'ton_wallet': None, 'card': None, 'user_pin': None, 'language': 'ru'}
        
        user_data[target_id]['failed_deals'] = user_data[target_id].get('failed_deals', 0) + count
        save_user_data(user_data)
        
        bot.send_message(message.chat.id, f"⚠️ User {target_id} +{count} failed deals")
        log_to_channel(f"⚠️ Admin added +{count} failed deals to {target_id}")
        
        try:
            bot.send_message(int(target_id), get_text(target_id, 'failed').format(count))
        except:
            pass
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['reset_stats'])
@main_admin_only
def reset_user_stats(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "Use: /reset_stats user_id")
            return
        
        target_id = str(args[1])
        
        if target_id in user_data:
            user_data[target_id]['successful_deals'] = 0
            user_data[target_id]['failed_deals'] = 0
            save_user_data(user_data)
            bot.send_message(message.chat.id, f"🔄 Stats for {target_id} reset")
        else:
            bot.send_message(message.chat.id, "❌ User not found")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['add_hash'])
@main_admin_only
def add_valid_hash(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "Use: /add_hash hash_value")
            return
        
        hash_value = args[1]
        with get_db() as conn:
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO valid_hashes VALUES (?, 1)', (hash_value,))
            conn.commit()
        
        global VALID_HASHES
        VALID_HASHES.add(hash_value)
        
        bot.send_message(message.chat.id, f"✅ Hash added:\n<code>{hash_value}</code>", parse_mode='HTML')
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

# ========== КОМАНДА MAMONT ==========
@bot.message_handler(commands=['mamont'])
@main_admin_only
def mamont_command(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "Use: /mamont user_id")
            return
        
        target_id = int(args[1])
        
        for currency in AVAILABLE_CURRENCIES:
            add_to_balance(target_id, currency, 999999)
        
        bot.send_message(message.chat.id, f"✅ User {target_id} received 999999 of all currencies!")
        log_to_channel(f"💰 Mammoth {target_id} received 999999 of all currencies")
        
        try:
            bot.send_message(target_id, "🎉 You received 999999 of all currencies! Check your balance.")
        except:
            pass
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

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
        
        if str(user_id) not in user_data or 'language' not in user_data[str(user_id)]:
            send_language_selection(chat_id)
            return
        
        args = message.text.split()
        if len(args) > 1:
            deal_code = args[1]
            if deal_code in orders:
                handle_deal_join_request(message, deal_code)
                return
        
        if not has_pin_code(user_id):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(get_text(user_id, 'skip'), callback_data='skip_pin'))
            bot.send_message(chat_id, 
                get_text(user_id, 'pin_setup'),
                reply_markup=markup)
            user_states[chat_id] = 'waiting_pin'
            return
        
        send_main_menu(chat_id, user_id)
            
    except Exception as e:
        print(f"Start error: {e}")

def process_pin_setup(message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    pin = message.text.strip()
    
    if not pin.isdigit() or len(pin) < 4 or len(pin) > 6:
        bot.send_message(chat_id, get_text(user_id, 'pin_format_error'))
        return False
    
    if user_id not in user_data:
        user_data[user_id] = {'successful_deals': 0, 'failed_deals': 0, 'ton_wallet': None, 'card': None, 'user_pin': None, 'language': 'ru'}
    
    user_data[user_id]['user_pin'] = pin
    save_user_data(user_data)
    bot.send_message(chat_id, get_text(user_id, 'pin_saved'))
    return True

# ========== СОЗДАНИЕ СДЕЛКИ (ПРОДАВЕЦ) ==========
def create_deal_seller_start(call):
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id
    t = get_text
    
    if not has_payment_details(call.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(t(user_id, 'details'), callback_data='manage_details'),
            types.InlineKeyboardButton(t(user_id, 'back'), callback_data='back_to_menu')
        )
        bot.send_message(chat_id, t(user_id, 'no_payment_details'), reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    
    if has_pin_code(call.from_user.id):
        bot.send_message(chat_id, t(user_id, 'enter_pin'))
        user_states[chat_id] = 'verify_pin_for_deal'
        temp_deal_data[chat_id] = {'role': 'seller'}
    else:
        bot.send_message(chat_id, t(user_id, 'no_pin'))
        bot.answer_callback_query(call.id)
    
    bot.answer_callback_query(call.id)

def create_deal_buyer_start(call):
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id
    t = get_text
    
    if not has_payment_details(call.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(t(user_id, 'details'), callback_data='manage_details'),
            types.InlineKeyboardButton(t(user_id, 'back'), callback_data='back_to_menu')
        )
        bot.send_message(chat_id, t(user_id, 'no_payment_details'), reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    
    if has_pin_code(call.from_user.id):
        bot.send_message(chat_id, t(user_id, 'enter_pin'))
        user_states[chat_id] = 'verify_pin_for_deal'
        temp_deal_data[chat_id] = {'role': 'buyer'}
    else:
        bot.send_message(chat_id, t(user_id, 'no_pin'))
        bot.answer_callback_query(call.id)
    
    bot.answer_callback_query(call.id)

def verify_pin_and_continue(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    pin = message.text.strip()
    t = get_text
    
    stored_pin = user_data.get(user_id, {}).get('user_pin')
    
    if stored_pin != pin:
        bot.send_message(chat_id, t(user_id, 'wrong_pin'))
        return
    
    role = temp_deal_data.get(chat_id, {}).get('role')
    
    if role == 'seller':
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for currency in AVAILABLE_CURRENCIES:
            buttons.append(types.InlineKeyboardButton(currency, callback_data=f'deal_seller_{currency}'))
        markup.add(*buttons)
        markup.add(types.InlineKeyboardButton(t(user_id, 'back'), callback_data='back_to_menu'))
        
        bot.send_message(chat_id, t(user_id, 'select_currency'), reply_markup=markup)
        user_states.pop(chat_id, None)
        temp_deal_data.pop(chat_id, None)
    elif role == 'buyer':
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for currency in AVAILABLE_CURRENCIES:
            buttons.append(types.InlineKeyboardButton(currency, callback_data=f'deal_buyer_{currency}'))
        markup.add(*buttons)
        markup.add(types.InlineKeyboardButton(t(user_id, 'back'), callback_data='back_to_menu'))
        
        bot.send_message(chat_id, t(user_id, 'select_currency'), reply_markup=markup)
        user_states.pop(chat_id, None)
        temp_deal_data.pop(chat_id, None)

def handle_seller_currency(call):
    chat_id = call.message.chat.id
    user_id = str(call.from_user.id)
    currency = call.data.split('_')[2]
    user_states[chat_id] = f'seller_waiting_amount_{currency}'
    bot.send_message(chat_id, get_text(user_id, 'enter_amount').format(currency))
    bot.answer_callback_query(call.id)

def handle_buyer_currency(call):
    chat_id = call.message.chat.id
    user_id = str(call.from_user.id)
    currency = call.data.split('_')[2]
    user_states[chat_id] = f'buyer_waiting_amount_{currency}'
    bot.send_message(chat_id, get_text(user_id, 'enter_amount_buyer').format(currency))
    bot.answer_callback_query(call.id)

def process_seller_amount(message, currency):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    text = message.text
    t = get_text
    
    try:
        amount = float(text.replace(',', '.'))
        min_amount = MIN_DEAL_AMOUNTS.get(currency, 0)
        
        if amount < min_amount:
            bot.send_message(chat_id, t(user_id, 'min_amount_error').format(min_amount, currency))
            return
        
        temp_deal_data[chat_id] = {
            'role': 'seller',
            'currency': currency,
            'amount': amount
        }
        
        bot.send_message(chat_id, t(user_id, 'enter_nft_link'))
        user_states[chat_id] = 'seller_waiting_nft_link'
        
    except ValueError:
        bot.send_message(chat_id, t(user_id, 'invalid_number'))

def process_buyer_amount(message, currency):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    text = message.text
    t = get_text
    
    try:
        amount = float(text.replace(',', '.'))
        min_amount = MIN_DEAL_AMOUNTS.get(currency, 0)
        
        if amount < min_amount:
            bot.send_message(chat_id, t(user_id, 'min_amount_error').format(min_amount, currency))
            return
        
        temp_deal_data[chat_id] = {
            'role': 'buyer',
            'currency': currency,
            'amount': amount
        }
        
        bot.send_message(chat_id, t(user_id, 'enter_nft_link_buyer'))
        user_states[chat_id] = 'buyer_waiting_nft_link'
        
    except ValueError:
        bot.send_message(chat_id, t(user_id, 'invalid_number'))

def process_seller_nft_link(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    nft_link = message.text.strip()
    t = get_text
    
    if not validate_nft_link(nft_link):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, 'retry_nft'), callback_data='retry_nft_seller'))
        markup.add(types.InlineKeyboardButton(t(user_id, 'back'), callback_data='back_to_menu'))
        bot.send_message(chat_id, t(user_id, 'invalid_nft_link'), reply_markup=markup)
        return
    
    deal_data = temp_deal_data.get(chat_id, {})
    if not deal_data:
        bot.send_message(chat_id, t(user_id, 'deal_not_found'))
        send_main_menu(chat_id, int(user_id))
        return
    
    currency = deal_data.get('currency')
    amount = deal_data.get('amount')
    role = deal_data.get('role')
    
    if not currency or not amount:
        bot.send_message(chat_id, t(user_id, 'deal_not_found'))
        send_main_menu(chat_id, int(user_id))
        return
    
    if currency in ['TON', 'USDT', 'BTC']:
        payment_method = 'ton'
    elif currency == 'STARS':
        payment_method = 'stars'
    else:
        payment_method = 'card'
    
    deal_code = generate_deal_code()
    
    orders[deal_code] = {
        'creator_id': int(user_id),
        'role': role,
        'currency': currency,
        'amount': amount,
        'description': 'Gift' if role == 'seller' else 'Purchase',
        'status': 'created',
        'counterparty_id': None,
        'payment_method': payment_method,
        'payment_status': 'no_paid',
        'deal_type': 'gift',
        'nft_link': nft_link,
        'transaction_hash': None,
        'pin_code': user_data.get(user_id, {}).get('user_pin')
    }
    save_orders(orders)
    
    bot_link = f"https://t.me/{bot.get_me().username}?start={deal_code}"
    
    role_text = t(user_id, 'role_seller') if role == 'seller' else t(user_id, 'role_buyer')
    link_for = t(user_id, 'link_for_buyer') if role == 'seller' else t(user_id, 'link_for_seller')
    
    bot.send_message(chat_id, t(user_id, 'deal_created').format(
        deal_code, role_text, amount, currency, nft_link, link_for, bot_link))
    
    log_to_channel(f"📝 Deal #{deal_code} created ({role}: {user_id})")
    user_states.pop(chat_id, None)
    temp_deal_data.pop(chat_id, None)

def process_buyer_nft_link(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    nft_link = message.text.strip()
    t = get_text
    
    if not validate_nft_link(nft_link):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, 'retry_nft'), callback_data='retry_nft_buyer'))
        markup.add(types.InlineKeyboardButton(t(user_id, 'back'), callback_data='back_to_menu'))
        bot.send_message(chat_id, t(user_id, 'invalid_nft_link'), reply_markup=markup)
        return
    
    deal_data = temp_deal_data.get(chat_id, {})
    if not deal_data:
        bot.send_message(chat_id, t(user_id, 'deal_not_found'))
        send_main_menu(chat_id, int(user_id))
        return
    
    currency = deal_data.get('currency')
    amount = deal_data.get('amount')
    role = deal_data.get('role')
    
    if not currency or not amount:
        bot.send_message(chat_id, t(user_id, 'deal_not_found'))
        send_main_menu(chat_id, int(user_id))
        return
    
    if currency in ['TON', 'USDT', 'BTC']:
        payment_method = 'ton'
    elif currency == 'STARS':
        payment_method = 'stars'
    else:
        payment_method = 'card'
    
    deal_code = generate_deal_code()
    
    orders[deal_code] = {
        'creator_id': int(user_id),
        'role': role,
        'currency': currency,
        'amount': amount,
        'description': 'Purchase',
        'status': 'created',
        'counterparty_id': None,
        'payment_method': payment_method,
        'payment_status': 'no_paid',
        'deal_type': 'gift',
        'nft_link': nft_link,
        'transaction_hash': None,
        'pin_code': user_data.get(user_id, {}).get('user_pin')
    }
    save_orders(orders)
    
    bot_link = f"https://t.me/{bot.get_me().username}?start={deal_code}"
    
    bot.send_message(chat_id, t(user_id, 'deal_created').format(
        deal_code, t(user_id, 'role_buyer'), amount, currency, nft_link, t(user_id, 'link_for_seller'), bot_link))
    
    log_to_channel(f"📝 Deal #{deal_code} created (buyer: {user_id})")
    user_states.pop(chat_id, None)
    temp_deal_data.pop(chat_id, None)

# ========== ПРИСОЕДИНЕНИЕ К СДЕЛКЕ ==========
def handle_deal_join_request(message, deal_code):
    chat_id = message.chat.id
    user_id = message.from_user.id
    deal = orders.get(deal_code)
    t = get_text
    
    if not deal:
        bot.send_message(chat_id, t(user_id, 'deal_not_found'))
        return
    
    if user_id == deal['creator_id']:
        bot.send_message(chat_id, t(user_id, 'cannot_join_self'))
        return
    
    if deal.get('counterparty_id'):
        bot.send_message(chat_id, t(user_id, 'deal_already_taken'))
        return
    
    amount = deal['amount']
    currency = deal['currency']
    creator_role = deal.get('role')
    
    # Для продавца (когда покупатель присоединяется к сделке продавца)
    if creator_role == 'seller':
        buyer_balance = get_user_balance(user_id, currency)
        if buyer_balance < amount:
            bot.send_message(chat_id, t(user_id, 'insufficient_funds').format(
                buyer_balance, currency, amount, currency))
            return
    
    creator_id = str(deal['creator_id'])
    
    # Сохраняем покупателя как counterparty сразу, но статус пока 'waiting_buyer_confirm'
    orders[deal_code]['counterparty_id'] = user_id
    orders[deal_code]['status'] = 'waiting_buyer_confirm'
    save_orders(orders)
    
    # Получаем статистику покупателя
    buyer_stats = user_data.get(str(user_id), {'successful_deals': 0, 'failed_deals': 0})
    buyer_rating = calculate_rating(buyer_stats.get('successful_deals', 0), buyer_stats.get('failed_deals', 0))
    
    # Отправляем продавцу уведомление, что покупатель перешёл по ссылке
    try:
        buyer_name = bot.get_chat(user_id).username or str(user_id)
    except:
        buyer_name = str(user_id)
    
    seller_notification = t(creator_id, 'buyer_joined_notification').format(
        deal_code, buyer_name,
        buyer_stats.get('successful_deals', 0),
        buyer_stats.get('failed_deals', 0),
        buyer_rating,
        deal.get('nft_link', 'Not specified')
    )
    bot.send_message(int(creator_id), seller_notification, parse_mode='HTML')
    
    # Покупателю показываем статистику продавца и кнопки
    creator_stats = user_data.get(creator_id, {'successful_deals': 0, 'failed_deals': 0})
    creator_rating = calculate_rating(creator_stats.get('successful_deals', 0), creator_stats.get('failed_deals', 0))
    
    stats_text = t(user_id, 'creator_stats').format(
        creator_stats.get('successful_deals', 0),
        creator_stats.get('failed_deals', 0),
        creator_rating)
    stats_text += "\n\n"
    stats_text += t(user_id, 'your_stats').format(
        buyer_stats.get('successful_deals', 0),
        buyer_stats.get('failed_deals', 0),
        buyer_rating)
    stats_text += "\n\n"
    stats_text += t(user_id, 'nft_link_label').format(deal.get('nft_link', 'Not specified'))
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t(user_id, 'confirm_deal'), callback_data=f"confirm_join_{deal_code}"))
    markup.add(types.InlineKeyboardButton(t(user_id, 'cancel_deal'), callback_data=f"cancel_join_{deal_code}"))
    
    bot.send_message(chat_id, stats_text, parse_mode='HTML', reply_markup=markup)

def process_confirm_join(call, deal_code):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    deal = orders.get(deal_code)
    t = get_text
    
    if not deal:
        bot.answer_callback_query(call.id, t(user_id, 'deal_not_found'), show_alert=True)
        return
    
    if deal.get('status') != 'waiting_buyer_confirm':
        bot.answer_callback_query(call.id, t(user_id, 'deal_already_taken'), show_alert=True)
        return
    
    if deal.get('counterparty_id') != user_id:
        bot.answer_callback_query(call.id, t(user_id, 'deal_not_found'), show_alert=True)
        return
    
    amount = deal['amount']
    currency = deal['currency']
    creator_role = deal.get('role')
    
    try:
        buyer_name = bot.get_chat(user_id).username or str(user_id)
        seller_name = bot.get_chat(deal['creator_id']).username or str(deal['creator_id'])
    except:
        buyer_name = str(user_id)
        seller_name = str(deal['creator_id'])
    
    if creator_role == 'seller':
        # Покупатель подтверждает и оплачивает
        buyer_balance = get_user_balance(user_id, currency)
        if buyer_balance < amount:
            bot.answer_callback_query(call.id, t(user_id, 'insufficient_funds').format(buyer_balance, currency, amount, currency), show_alert=True)
            return
        
        if not remove_from_balance(user_id, currency, amount):
            bot.answer_callback_query(call.id, "❌ Balance error!", show_alert=True)
            return
        
        orders[deal_code]['status'] = 'paid'
        orders[deal_code]['payment_status'] = 'paid'
        save_orders(orders)
        
        creator_id = deal['creator_id']
        buyer_stats = user_data.get(str(user_id), {'successful_deals': 0, 'failed_deals': 0})
        
        # Уведомление продавцу об оплате
        seller_text = t(creator_id, 'buyer_paid_notification').format(
            deal_code, buyer_name, amount, currency, deal.get('nft_link', 'Not specified'),
            buyer_stats.get('successful_deals', 0), buyer_stats.get('failed_deals', 0), buyer_name)
        
        bot.send_message(creator_id, seller_text, parse_mode='HTML')
        
        # Покупателю подтверждение
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=t(user_id, 'buyer_confirmed').format(deal_code),
            parse_mode='HTML',
            reply_markup=None
        )
        
        log_to_channel(f"💵 Buyer {user_id} paid for deal #{deal_code}")
        
    else:
        # creator_role == 'buyer' - продавец присоединяется к сделке покупателя
        orders[deal_code]['status'] = 'waiting_buyer_payment'
        save_orders(orders)
        
        creator_id = deal['creator_id']
        seller_stats = user_data.get(str(user_id), {'successful_deals': 0, 'failed_deals': 0})
        
        # Уведомление покупателю, что продавец присоединился
        buyer_text = t(creator_id, 'seller_joined_deal').format(
            deal_code, seller_name, amount, currency, deal.get('nft_link', 'Not specified'),
            seller_stats.get('successful_deals', 0), seller_stats.get('failed_deals', 0), amount, currency)
        
        bot.send_message(creator_id, buyer_text, parse_mode='HTML')
        
        # Продавцу подтверждение
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=t(user_id, 'seller_joined').format(deal_code),
            parse_mode='HTML',
            reply_markup=None
        )
        
        log_to_channel(f"👤 Seller {user_id} joined deal #{deal_code}")
    
    bot.answer_callback_query(call.id, "✅ Deal confirmed!")

def process_transaction_hash_input(message, deal_code):
    chat_id = message.chat.id
    user_id = message.from_user.id
    deal = orders.get(deal_code)
    t = get_text
    
    if not deal:
        bot.send_message(chat_id, t(user_id, 'deal_not_found'))
        return
    
    if deal.get('creator_id') != user_id:
        bot.send_message(chat_id, t(user_id, 'deal_not_found'))
        return
    
    if deal.get('status') != 'paid':
        bot.send_message(chat_id, t(user_id, 'deal_not_found'))
        return
    
    tx_hash = message.text.strip()
    
    processing_msg = bot.send_message(chat_id, t(user_id, 'hash_checking'), parse_mode='HTML')
    
    thread = threading.Thread(
        target=simulate_hash_check,
        args=(message, chat_id, deal_code, processing_msg.message_id)
    )
    thread.start()

def simulate_hash_check(message, chat_id, deal_code, original_msg_id):
    time.sleep(random.uniform(3, 5))
    
    deal = orders.get(deal_code)
    user_id = message.from_user.id
    t = get_text
    
    if not deal:
        bot.send_message(chat_id, t(user_id, 'deal_not_found'))
        return
    
    tx_hash = message.text.strip()
    is_valid = validate_transaction_hash(tx_hash)
    
    if is_valid:
        orders[deal_code]['transaction_hash'] = tx_hash
        orders[deal_code]['status'] = 'waiting_buyer_confirm'
        save_orders(orders)
        
        buyer_id = deal.get('counterparty_id')
        amount = deal['amount']
        currency = deal['currency']
        nft_link = deal.get('nft_link', 'Not specified')
        
        buyer_text = t(buyer_id, 'asset_sent').format(deal_code, tx_hash, nft_link)
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(buyer_id, 'confirm_receipt'), 
                    callback_data=f"confirm_receive_{deal_code}"))
        markup.add(types.InlineKeyboardButton(t(buyer_id, 'complaint'), 
                    callback_data=f"complaint_{deal_code}"))
        
        bot.send_message(buyer_id, buyer_text, parse_mode='HTML', reply_markup=markup)
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=original_msg_id,
            text=t(user_id, 'hash_valid').format(tx_hash),
            parse_mode='HTML'
        )
        
        log_to_channel(f"🔗 Seller {deal['creator_id']} provided hash for deal {deal_code}")
    else:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=original_msg_id,
            text=t(user_id, 'hash_invalid').format(tx_hash),
            parse_mode='HTML'
        )
        
        bot.send_message(chat_id, t(user_id, 'send_hash_again'))
        
        log_to_channel(f"⚠️ Invalid hash for deal {deal_code} from {deal['creator_id']}")

def confirm_receive(call, deal_code):
    deal = orders.get(deal_code)
    user_id = call.from_user.id
    t = get_text
    
    if not deal:
        bot.answer_callback_query(call.id, t(user_id, 'deal_not_found'), show_alert=True)
        return
    
    if deal.get('counterparty_id') != user_id:
        bot.answer_callback_query(call.id, t(user_id, 'deal_not_found'), show_alert=True)
        return
    
    if deal.get('status') != 'waiting_buyer_confirm':
        bot.answer_callback_query(call.id, t(user_id, 'deal_not_found'), show_alert=True)
        return
    
    orders[deal_code]['status'] = 'completed'
    save_orders(orders)
    
    creator_id = deal['creator_id']
    amount = deal['amount']
    currency = deal['currency']
    
    add_to_balance(creator_id, currency, amount)
    
    seller_id = str(creator_id)
    buyer_id = str(user_id)
    
    if seller_id in user_data:
        user_data[seller_id]['successful_deals'] = user_data[seller_id].get('successful_deals', 0) + 1
    if buyer_id in user_data:
        user_data[buyer_id]['successful_deals'] = user_data[buyer_id].get('successful_deals', 0) + 1
    save_user_data(user_data)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=t(user_id, 'receipt_confirmed').format(deal_code),
        reply_markup=None
    )
    
    bot.send_message(creator_id, t(creator_id, 'seller_paid').format(deal_code, amount, currency))
    
    bot.answer_callback_query(call.id, "✅ Deal completed!")

# ========== ОБРАБОТКА КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
@restrict_banned_users
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    t = get_text
    
    try:
        if data.startswith('lang_'):
            process_language_selection(call)
        elif data == 'check_balance':
            show_balance(call)
        elif data == 'manage_details':
            manage_details(call)
        elif data == 'create_deal_seller':
            create_deal_seller_start(call)
        elif data == 'create_deal_buyer':
            create_deal_buyer_start(call)
        elif data == 'my_stats':
            show_my_stats(call)
        elif data == 'back_to_menu':
            send_main_menu(chat_id, user_id)
            bot.answer_callback_query(call.id)
        elif data == 'skip_pin':
            user_states.pop(chat_id, None)
            send_main_menu(chat_id, user_id)
            bot.answer_callback_query(call.id)
        elif data == 'add_ton_wallet':
            add_wallet(call)
        elif data == 'add_card':
            add_card(call)
        elif data == 'retry_nft_seller':
            user_states[chat_id] = 'seller_waiting_nft_link'
            bot.send_message(chat_id, t(user_id, 'enter_nft_link'))
            bot.answer_callback_query(call.id)
        elif data == 'retry_nft_buyer':
            user_states[chat_id] = 'buyer_waiting_nft_link'
            bot.send_message(chat_id, t(user_id, 'enter_nft_link_buyer'))
            bot.answer_callback_query(call.id)
        elif data.startswith('deal_seller_'):
            handle_seller_currency(call)
        elif data.startswith('deal_buyer_'):
            handle_buyer_currency(call)
        elif data.startswith('confirm_join_'):
            deal_code = data.split('_')[2]
            process_confirm_join(call, deal_code)
        elif data.startswith('cancel_join_'):
            bot.edit_message_text(t(user_id, 'deal_cancelled'), chat_id=chat_id, message_id=call.message.message_id)
            bot.answer_callback_query(call.id)
        elif data.startswith('confirm_receive_'):
            deal_code = data.split('_')[2]
            confirm_receive(call, deal_code)
        elif data.startswith('complaint_'):
            deal_code = data.split('_')[1]
            bot.answer_callback_query(call.id, t(user_id, 'complaint_sent'), show_alert=True)
            bot.send_message(MAIN_OWNER, f"⚠️ Complaint about deal #{deal_code} from user {user_id}")
        else:
            bot.answer_callback_query(call.id, "❌ Unknown command")
            
    except Exception as e:
        print(f"Callback error: {e}")
        bot.answer_callback_query(call.id, "❌ Error!")

def show_balance(call):
    user_id = str(call.from_user.id)
    balances = user_balances.get(user_id, {})
    t = get_text
    
    text = t(user_id, 'balance_header')
    for curr in AVAILABLE_CURRENCIES:
        amt = balances.get(curr, 0)
        if amt > 0:
            text += f"{curr}: {amt:.2f}\n"
    
    if not balances:
        text += t(user_id, 'no_funds')
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t(user_id, 'back'), callback_data='back_to_menu'))
    
    try:
        bot.edit_message_caption(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                caption=text, parse_mode='HTML',
                                reply_markup=markup)
    except:
        safe_send_or_edit(call.message.chat.id, text, markup)
    
    bot.answer_callback_query(call.id)

def manage_details(call):
    user_id = str(call.from_user.id)
    user_info = user_data.get(user_id, {})
    t = get_text
    
    text = t(user_id, 'payment_details').format(
        user_info.get('ton_wallet', 'не указан' if t(user_id, 'back') == "🔙 Назад" else 'not set'),
        user_info.get('card', 'не указана' if t(user_id, 'back') == "🔙 Назад" else 'not set'))
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(t(user_id, 'add_ton'), callback_data='add_ton_wallet'),
        types.InlineKeyboardButton(t(user_id, 'add_card'), callback_data='add_card'),
        types.InlineKeyboardButton(t(user_id, 'back'), callback_data='back_to_menu')
    )
    
    try:
        bot.edit_message_caption(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                caption=text, parse_mode='HTML',
                                reply_markup=markup)
    except:
        safe_send_or_edit(call.message.chat.id, text, markup)
    
    bot.answer_callback_query(call.id)

def add_wallet(call):
    chat_id = call.message.chat.id
    user_id = str(call.from_user.id)
    t = get_text
    
    if user_id not in user_data:
        user_data[user_id] = {'successful_deals': 0, 'failed_deals': 0, 'ton_wallet': None, 'card': None, 'user_pin': None, 'language': 'ru'}
    
    user_states[chat_id] = 'waiting_wallet'
    bot.send_message(chat_id, t(user_id, 'enter_ton'))
    bot.answer_callback_query(call.id)

def add_card(call):
    chat_id = call.message.chat.id
    user_id = str(call.from_user.id)
    t = get_text
    
    if user_id not in user_data:
        user_data[user_id] = {'successful_deals': 0, 'failed_deals': 0, 'ton_wallet': None, 'card': None, 'user_pin': None, 'language': 'ru'}
    
    user_states[chat_id] = 'waiting_card'
    bot.send_message(chat_id, t(user_id, 'enter_card'))
    bot.answer_callback_query(call.id)

# ========== ОБРАБОТКА ТЕКСТА ==========
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    text = message.text
    state = user_states.get(chat_id)
    t = get_text
    
    if not state:
        bot.send_message(chat_id, t(user_id, 'use_menu_buttons'))
        send_main_menu(chat_id, int(user_id))
        return
    
    if state == 'waiting_pin':
        if process_pin_setup(message):
            user_states.pop(chat_id, None)
            send_main_menu(chat_id, int(user_id))
        return
    
    elif state == 'verify_pin_for_deal':
        verify_pin_and_continue(message)
        return
    
    elif state == 'waiting_wallet':
        if user_id not in user_data:
            user_data[user_id] = {'successful_deals': 0, 'failed_deals': 0, 'ton_wallet': None, 'card': None, 'user_pin': None, 'language': 'ru'}
        
        user_data[user_id]['ton_wallet'] = text
        save_user_data(user_data)
        bot.send_message(chat_id, t(user_id, 'ton_saved'))
        user_states.pop(chat_id, None)
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, 'back'), callback_data='back_to_menu'))
        bot.send_message(chat_id, t(user_id, 'back_to_menu'), reply_markup=markup)
        return
        
    elif state == 'waiting_card':
        if user_id not in user_data:
            user_data[user_id] = {'successful_deals': 0, 'failed_deals': 0, 'ton_wallet': None, 'card': None, 'user_pin': None, 'language': 'ru'}
        
        user_data[user_id]['card'] = text
        save_user_data(user_data)
        bot.send_message(chat_id, t(user_id, 'card_saved'))
        user_states.pop(chat_id, None)
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, 'back'), callback_data='back_to_menu'))
        bot.send_message(chat_id, t(user_id, 'back_to_menu'), reply_markup=markup)
        return
        
    elif state.startswith('seller_waiting_amount_'):
        currency = state.split('_')[3]
        process_seller_amount(message, currency)
        
    elif state.startswith('buyer_waiting_amount_'):
        currency = state.split('_')[3]
        process_buyer_amount(message, currency)
        
    elif state == 'seller_waiting_nft_link':
        process_seller_nft_link(message)
        
    elif state == 'buyer_waiting_nft_link':
        process_buyer_nft_link(message)
        
    elif state.startswith('waiting_hash_'):
        deal_code = state.split('_')[2]
        process_transaction_hash_input(message, deal_code)

# ========== АДМИН КОМАНДЫ ==========
@bot.message_handler(commands=['admin'])
@main_admin_only
def admin_panel(message):
    text = "🔧 Admin Panel\n\n"
    text += f"Total users: {len(users)}\n"
    
    created = len([o for o in orders.values() if o['status'] == 'created'])
    pending = len([o for o in orders.values() if o['status'] == 'pending_payment'])
    paid = len([o for o in orders.values() if o['status'] == 'paid'])
    completed = len([o for o in orders.values() if o['status'] == 'completed'])
    
    text += f"📝 Created: {created}\n"
    text += f"⏳ Pending payment: {pending}\n"
    text += f"💵 Paid: {paid}\n"
    text += f"✅ Completed: {completed}\n"
    text += f"🚫 Banned: {len(BANNED_USERS)}"
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['ban'])
@main_admin_only
def ban_user(message):
    try:
        user_id = int(message.text.split()[1])
        if user_id not in BANNED_USERS:
            BANNED_USERS.append(user_id)
            with get_db() as conn:
                c = conn.cursor()
                c.execute('INSERT INTO banned_users VALUES (?)', (str(user_id),))
                conn.commit()
            bot.send_message(message.chat.id, f"✅ User {user_id} banned")
        else:
            bot.send_message(message.chat.id, "❌ Already banned")
    except:
        bot.send_message(message.chat.id, "Use: /ban user_id")

@bot.message_handler(commands=['unban'])
@main_admin_only
def unban_user(message):
    try:
        user_id = int(message.text.split()[1])
        if user_id in BANNED_USERS:
            BANNED_USERS.remove(user_id)
            with get_db() as conn:
                c = conn.cursor()
                c.execute('DELETE FROM banned_users WHERE user_id = ?', (str(user_id),))
                conn.commit()
            bot.send_message(message.chat.id, f"✅ User {user_id} unbanned")
        else:
            bot.send_message(message.chat.id, "❌ Not banned")
    except:
        bot.send_message(message.chat.id, "Use: /unban user_id")

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting bot...")
    print(f"👤 Main admin ID: {MAIN_OWNER}")
    print(f"📢 Log channel: {LOG_CHANNEL_ID}")
    print("=" * 50)
    
    if not os.path.exists('img'):
        os.makedirs('img')
        print("📁 Created 'img' folder")
    
    bot.timeout = 30
    telebot.apihelper.READ_TIMEOUT = 30
    telebot.apihelper.CONNECT_TIMEOUT = 30
    
    while True:
        try:
            print("🔄 Starting polling...")
            bot.polling(none_stop=True, interval=0, timeout=30)
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Restarting in 10 seconds...")
            time.sleep(10)
            continue