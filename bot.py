import asyncio
import os
from io import BytesIO

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BufferedInputFile
from dotenv import load_dotenv

from PIL import Image, ImageDraw, ImageFont

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🔥 WB Infocard AI Bot\n\n"
        "Отправь фото товара с подписью — я создам инфокарточку WB 900x1200 PNG"
    )


@dp.message(F.photo)
async def create_infocard(message: Message):

    caption = message.caption or "Товар Wildberries"

    photo = message.photo[-1]

    file = await bot.get_file(photo.file_id)

    file_bytes = await bot.download_file(file.file_path)

    product_image = Image.open(file_bytes).convert("RGBA")

    canvas = Image.new("RGB", (900, 1200), "white")

    draw = ImageDraw.Draw(canvas)

    try:
        font_title = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            44
        )

        font_text = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            30
        )

    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    draw.rounded_rectangle(
        (40, 40, 860, 170),
        radius=40,
        fill=(8, 22, 45)
    )

    draw.text(
        (70, 75),
        "WB INFOCARD",
        font=font_title,
        fill="white"
    )

    product_image.thumbnail((650, 650))

    px = (900 - product_image.width) // 2
    py = 230

    canvas.paste(product_image, (px, py), product_image)

    draw.rounded_rectangle(
        (50, 930, 850, 1090),
        radius=35,
        fill=(240, 240, 240)
    )

    text = caption[:120]

    draw.text(
        (80, 980),
        text,
        font=font_text,
        fill=(20, 20, 20)
    )

    output = BytesIO()

    canvas.save(output, format="PNG")

    output.seek(0)

    image = BufferedInputFile(
        output.read(),
        filename="wb_infocard.png"
    )

    await message.answer_photo(
        image,
        caption="✅ Готово: инфокарточка WB 900x1200 PNG"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())