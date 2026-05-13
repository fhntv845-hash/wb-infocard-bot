import asyncio
import os
from io import BytesIO

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]

    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            pass

    return ImageFont.load_default()


@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer(
        "🔥 WB Infocard AI Bot\n\n"
        "Отправь фото товара с подписью — я создам инфокарточку WB 900×1200 PNG."
    )


@dp.message(F.photo | F.document)
async def handle_photo(message: Message):
    await message.answer("🖼 Создаю инфокарточку...")

    if message.photo:
        file_id = message.photo[-1].file_id
    else:
        file_id = message.document.file_id

    file = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file.file_path)

    image = Image.open(downloaded_file).convert("RGB")
    image = image.resize((900, 1200))

    draw = ImageDraw.Draw(image)

    title_font = font(48, True)
    text_font = font(32, True)

    title = "ИНФОКАРТОЧКА WB"
    product_text = message.caption or "Товар для Wildberries"

    draw.rounded_rectangle(
        (30, 30, 870, 170),
        radius=40,
        fill=(10, 20, 35)
    )

    draw.text(
        (60, 75),
        title,
        font=title_font,
        fill="white"
    )

    draw.rounded_rectangle(
        (40, 980, 860, 1140),
        radius=30,
        fill=(240, 240, 240)
    )

    draw.text(
        (70, 1030),
        product_text[:90],
        font=text_font,
        fill="black"
    )

    output_path = "wb_infocard.png"
    image.save(output_path)

    await message.answer_document(
        FSInputFile(output_path),
        caption="✅ Готово: инфокарточка WB 900×1200 PNG"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())