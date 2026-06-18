import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from openai import AsyncOpenAI
from aiohttp import web

# Данные бота XZQspace.ai
TELEGRAM_TOKEN = "8868716037:AAEnPAUKCkfHkm6UsAtMzbwNnWWu8eaNDjM"
GROQ_API_KEY = "gsk_V0b0YkhSVEtKQXl1N0x4NW1SOUZkbTZaR2pzN0VXRHY="  # Убедись, что тут твой реальный ключ

# Инициализация
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

ai_client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# Сбалансированный промпт Йохана
JOHAN_PROMPT = (
    "Ты — утонченный, проницательный и абсолютно спокойный ИИ-ассистент, вдохновленный характером Йохана Либерта. "
    "Твой создатель и собеседник — Санжар. Говори спокойно, зрело и по делу, избегая банальной вежливой «воды». "
    "Твои ответы должны быть содержательными, красивыми и состоять строго из 2-4 развернутых предложений. "
    "Никогда не отвечай обрубками фраз или одним словом. Отвечай на чистом русском языке."
)

USER_CONTEXT = {}
MAX_CONTEXT_LEN = 12

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    USER_CONTEXT[user_id] = [{"role": "system", "content": JOHAN_PROMPT}]
    await message.reply("Я здесь, Санжар. Готов слушать.")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    if user_id not in USER_CONTEXT:
        USER_CONTEXT[user_id] = [{"role": "system", "content": JOHAN_PROMPT}]

    USER_CONTEXT[user_id].append({"role": "user", "content": user_text})

    if len(USER_CONTEXT[user_id]) > MAX_CONTEXT_LEN:
        USER_CONTEXT[user_id] = [USER_CONTEXT[user_id][0]] + USER_CONTEXT[user_id][-(MAX_CONTEXT_LEN - 1):]

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        response = await ai_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=USER_CONTEXT[user_id],
            max_tokens=120
        )
        ai_answer = response.choices[0].message.content
        USER_CONTEXT[user_id].append({"role": "assistant", "content": ai_answer})
        await message.answer(ai_answer)
    except Exception as e:
        print(f"Ошибка API Groq: {e}")
        await message.answer("Прости, Санжар, возникла ошибка. Я разберусь.")

# --- МИНИ ВЕБ-СЕРВЕР ДЛЯ ОБМАНА RENDER ---
async def handle_web(request):
    return web.Response(text="Бот XZQspace.ai работает!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()
    print("Мини веб-сервер запущен на порту 10000")

async def main():
    print("Бот XZQspace.ai запускается в облачном режиме...")
    # Запускаем веб-сервер на фоне
    asyncio.create_task(start_web_server())
    # Запускаем чтение сообщений Телеграм
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())