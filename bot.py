import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv

from PIL import Image, ImageDraw

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer(
        "🔥 WB Infocard AI Bot\n\n"
        "Отправь фото товара с подписью — "
        "я создам инфокарточку WB 900×1200 PNG"
    )


@dp.message(F.photo | F.document)
async def handle_photo(message: Message):

    await message.answer(
        "🖼 Анализирую фото и создаю инфокарточку..."
    )

    # Получаем file_id
    if message.photo:
        file_id = message.photo[-1].file_id
    else:
        file_id = message.document.file_id

    # Получаем файл
    file = await bot.get_file(file_id)

    # Скачиваем файл
    downloaded_file = await bot.download_file(file.file_path)

    # Открываем изображение
    image = Image.open(downloaded_file).convert("RGB")

    # Размер WB
    image = image.resize((900, 1200))

    draw = ImageDraw.Draw(image)

    # Верхняя тёмная плашка
    draw.rounded_rectangle(
        (30, 30, 870, 170),
        radius=40,
        fill=(10, 20, 35)
    )

    # Заголовок
    title = "WB INFOCARD"

    # Текст
    draw.text(
        (60, 80),
        title,
        fill="white"
    )

    # Подпись товара
    if message.caption:
        product_text = message.caption[:120]
    else:
        product_text = "Товар Wildberries"

    # Нижний блок
    draw.rounded_rectangle(
        (40, 980, 860, 1140),
        radius=30,
        fill=(240, 240, 240)
    )

    draw.text(
        (70, 1030),
        product_text,
        fill="black"
    )

    # Сохраняем
    output_path = "wb_infocard.png"

    image.save(output_path)

    # Отправляем файл
    await message.answer_document(
        FSInputFile(output_path),
        caption="✅ Готово: инфокарточка WB 900×1200 PNG"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())