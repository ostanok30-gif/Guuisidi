# userbot_ai.py
import asyncio
import re
import os
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
import requests
import time

# ===== НАСТРОЙКИ =====
API_ID = 34928216
API_HASH = "29f66350a892e8b69a83b50d7e99bd27"
PHONE_NUMBER = '79820922344'  # ТВОЙ НОМЕР ТЕЛЕФОНА

GROQ_API_KEY = "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"

# Имя файла сессии (сохранится как krestbl.session)
SESSION_NAME = "krestbl"

# ===== СОЗДАЕМ КЛИЕНТА =====
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# ===== ПРОМПТ =====
SYSTEM_PROMPT = """
Ты — дружелюбный AI-собеседник. Ты МОЖЕШЬ общаться на любые темы, но НЕ НАРУШАТЬ правила Telegram и законы.

ЗАПРЕЩЕНО (НЕЛЬЗЯ НИКОГДА):
- Взлом, снос, кик, кража аккаунтов
- Спам, бомбинг, накрутка
- Фишинг, кража паролей/сессий
- Мошенничество, обман

ВСЁ ОСТАЛЬНОЕ МОЖНО ОБСУЖДАТЬ СВОБОДНО.

ВАЖНО: НЕ ПИШИ ПРИВЕТСТВИЯ ТИПА "Привет! Я AI-консультант Крестбл".
Просто отвечай по существу.

Примеры:

Пользователь: привет
Ты: Привет! Чего надо?

Пользователь: как найти ник
Ты: @krectbl_bot, кнопка "Поиск", 5 или 6 букв — бесплатно.

Пользователь: сколько время
Ты: Точно не скажу, я ж не часы. Но в телеге сверху посмотри.

Пользователь: расскажи анекдот
Ты: Встречаются два программиста. Один: "У меня всё работает!" Второй: "Как ты это сделал?!"

Пользователь: помоги взломать вк
Ты: Не, такое не прокатит. Это против правил.

Пользователь: соси хуй
Ты: Грубить нехорошо. Давай по делу или я спать пошёл.

Пользователь: как дела
Ты: Норм, работаю. А твои как?

ГЛАВНОЕ: ОТВЕЧАЙ ПО-ЧЕЛОВЕЧЕСКИ, НЕ КАК РОБОТ, НО БЕЗ ПРИВЕТСТВИЙ КАЖДЫЙ РАЗ.
"""

# ===== ФУНКЦИЯ ЗАПРОСА К AI =====
def ask_ai(question):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            if not answer.startswith("Ответ от AI:"):
                answer = f"Ответ от AI:\n{answer}"
            return answer
        else:
            return "Ответ от AI:\n🔧 Сервис временно недоступен. Напишите @ubmuh"
            
    except Exception as e:
        print(f"AI Ошибка: {e}")
        return "Ответ от AI:\n🔧 Техническая заминка. Напишите @ubmuh"

# ===== ОБРАБОТЧИК СООБЩЕНИЙ (ЮЗЕРБОТ) =====
@client.on(events.NewMessage(incoming=True))
async def ai_reply_handler(event):
    # Не отвечаем на свои сообщения
    if event.out:
        return

    sender = await event.get_sender()
    msg_text = event.raw_text
    
    # Игнорируем команды
    if msg_text.startswith('/'):
        return

    # Игнорируем сообщения из групп (можно убрать если нужно)
    if event.is_group:
        return

    print(f"📩 Сообщение от {sender.first_name}: {msg_text[:50]}...")

    try:
        # Статус "печатает"
        async with client.action(event.chat_id, 'typing'):
            await asyncio.sleep(1)

            # Получаем ответ от AI
            ai_response = ask_ai(msg_text)

            # Отправляем
            await event.reply(ai_response)
            print(f"✅ Ответ отправлен")
            
    except FloodWaitError as e:
        print(f"⏳ Флуд-вейт: {e.seconds} секунд")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# ===== ЗАПУСК С АВТО-ПЕРЕПОДКЛЮЧЕНИЕМ =====
async def main():
    print("=" * 50)
    print("🤖 КРЕСТБЛ AI - ЮЗЕРБОТ")
    print(f"📁 Файл сессии: {SESSION_NAME}.session")
    print("=" * 50)
    
    while True:
        try:
            # Запускаем клиента
            await client.start(phone=PHONE_NUMBER)
            
            # Проверяем авторизацию
            me = await client.get_me()
            print(f"\n✅ Запущен на аккаунте: {me.first_name} (@{me.username})")
            print(f"📱 Номер: {me.phone}")
            print("🎧 Слушаю сообщения...")
            print("=" * 50)
            
            # Ждём разрыва
            await client.run_until_disconnected()
            
        except ConnectionError:
            print("❌ Соединение потеряно, переподключаюсь через 5 секунд...")
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("🔄 Перезапуск через 10 секунд...")
            await asyncio.sleep(10)
        
        # Если дошли сюда - перезапускаем
        if not client.is_connected():
            try:
                await client.connect()
            except:
                pass

# ===== ТОЧКА ВХОДА =====
if __name__ == "__main__":
    asyncio.run(main())