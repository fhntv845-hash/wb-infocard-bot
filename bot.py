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
        "Отправь название товара текстом — я создам SEO, описание и идеи для WB.\n\n"
        "Или отправь фото товара с подписью — я подготовлю ТЗ для инфокарточки."
    )


@dp.message(F.photo)
async def handle_photo(message: Message):
    caption = message.caption or "Описание товара не указано"

    await message.answer("🖼 Анализирую фото и готовлю ТЗ для инфокарточки WB...")

    prompt = f"""
Ты профессиональный дизайнер инфокарточек Wildberries и эксперт по маркетплейсам.

Пользователь отправил фото товара.
Описание пользователя: {caption}

Сделай подробное ТЗ для создания продающей инфокарточки WB 900x1200.

Важно:
— не придумывай лишние свойства товара
— не искажай товар
— товар должен остаться реалистичным
— текст не должен перекрывать товар
— стиль премиум, дорогой, чистый
— фон должен усиливать товар, но не отвлекать

СТРУКТУРА ОТВЕТА:

1. Главный заголовок карточки
До 35 символов, крупно, продающе.

2. Подзаголовок
Короткая выгода для покупателя.

3. Композиция 900x1200
— где разместить товар
— где разместить заголовок
— где разместить блоки
— как оставить товар открытым

4. 4 продающих блока на карточке
Формат:
Блок 1:
Заголовок:
Короткий текст:

5. Цвета и стиль
— фон
— цвета блоков
— стиль шрифтов
— премиум-эффекты

6. Текст, который должен быть на инфокарточке
Только короткие фразы, готовые для дизайна.

7. Промт для генерации фона/дизайна
Без изменения самого товара.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    await message.answer(response.text[:4000])


@dp.message(F.text)
async def generate_text(message: Message):
    user_text = message.text

    await message.answer("⌛ Генерирую WB-текст...")

    prompt = f"""
Ты профессиональный эксперт по Wildberries, инфокарточкам WB, SEO-продажам и маркетингу.

Товар: {user_text}

Сделай мощный продающий комплект для Wildberries.

СТРУКТУРА ОТВЕТА:

1. SEO-заголовок WB
— до 60 символов

2. 10 SEO-ключей
— через запятую

3. 7 преимуществ товара

4. Продающее описание товара

5. Текст для 5 слайдов инфокарточки

6. Профессиональный Kling AI prompt
— реалистичное видео товара
— стиль дорогой рекламы
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