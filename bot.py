import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from google import genai

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = genai.Client(api_key=GEMINI_API_KEY)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🔥 WB Infocard AI Bot\n\n"
        "Отправь название товара — я создам SEO-заголовок, преимущества и описание для WB."
    )


@dp.message(F.text)
async def generate_text(message: Message):
    user_text = message.text

    await message.answer("⏳ Генерирую WB-текст...")

    prompt = f"""
Ты эксперт по Wildberries, SEO и продающим инфокарточкам.

Товар: {user_text}

Сделай:
1. SEO-заголовок до 60 символов
2. 7 преимуществ для инфокарточки
3. Продающее описание товара
4. Текст для 5 слайдов WB
5. Промт для Kling AI для видео товара

Пиши на русском. Без воды. Максимально продающе.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    await message.answer(response.text[:4000])


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())