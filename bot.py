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
Ты профессиональный эксперт по Wildberries, инфокарточкам WB, SEO-продажам и маркетингу.

Товар: {user_text}

Сделай мощный продающий комплект для Wildberries.

СТРУКТУРА ОТВЕТА:

1. SEO-заголовок WB
— до 60 символов
— максимально продающий
— SEO-оптимизированный
— как у ТОП-1 продавцов

2. 10 SEO-ключей
— высокочастотные запросы WB
— через запятую

3. 7 преимуществ товара
— коротко
— мощно
— с акцентом на выгоду

4. Продающее описание товара
— стиль ТОП-карточек WB
— премиум подача
— высокая конверсия
— без воды

5. Текст для 5 слайдов инфокарточки
Формат:
Слайд 1:
Заголовок:
Подзаголовок:

6. Профессиональный Kling AI prompt
— реалистичное видео товара
— стиль дорогой рекламы
— cinematic
— premium lighting
— realistic water
— smooth camera motion
— vertical 9:16

Пиши максимально мощно и профессионально.
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