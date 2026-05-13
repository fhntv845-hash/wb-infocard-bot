import asyncio
import os
from io import BytesIO

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, BufferedInputFile
from dotenv import load_dotenv
from google import genai
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = genai.Client(api_key=GEMINI_API_KEY)


def get_font(size, bold=False):
    try:
        if bold:
            path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        else:
            path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

        return ImageFont.truetype(path, size)

    except:
        return ImageFont.load_default()


def wrap_text(draw, text, font, max_width):
    words = text.split()

    lines = []

    line = ""

    for word in words:
        test_line = line + word + " "

        bbox = draw.textbbox((0, 0), test_line, font=font)

        width = bbox[2]

        if width <= max_width:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "

    if line:
        lines.append(line.strip())

    return lines


def parse_ai_text(text):
    title = "Премиум товар для WB"

    blocks = [
        "Высокое качество",
        "Надёжная конструкция",
        "Готово к установке"
    ]

    for line in text.splitlines():

        line = line.strip()

        if line.startswith("ЗАГОЛОВОК:"):
            title = line.replace("ЗАГОЛОВОК:", "").strip()

        elif line.startswith("БЛОК1:"):
            blocks[0] = line.replace("БЛОК1:", "").strip()

        elif line.startswith("БЛОК2:"):
            blocks[1] = line.replace("БЛОК2:", "").strip()

        elif line.startswith("БЛОК3:"):
            blocks[2] = line.replace("БЛОК3:", "").strip()

    return title[:45], blocks


def create_infocard(product_bytes, title, blocks):

    W, H = 900, 1200

    card = Image.new("RGB", (W, H), (240, 244, 248))

    draw = ImageDraw.Draw(card)

    # Главный фон
    draw.rounded_rectangle(
        (25, 25, 875, 1175),
        radius=40,
        fill=(255, 255, 255)
    )

    # Верхний premium блок
    draw.rounded_rectangle(
        (40, 40, 860, 190),
        radius=35,
        fill=(10, 25, 45)
    )

    title_font = get_font(52, bold=True)

    block_font = get_font(34, bold=True)

    small_font = get_font(24)

    # Заголовок
    y = 70

    title_lines = wrap_text(
        draw,
        title,
        title_font,
        700
    )

    for line in title_lines:

        draw.text(
            (70, y),
            line,
            font=title_font,
            fill=(255, 255, 255)
        )

        y += 58

    draw.text(
        (70, 155),
        "Премиум качество • Wildberries",
        font=small_font,
        fill=(180, 205, 230)
    )

    # Фото товара
    product = Image.open(
        BytesIO(product_bytes)
    ).convert("RGBA")

    product.thumbnail(
        (620, 620),
        Image.LANCZOS
    )

    px = (W - product.width) // 2

    py = 250

    # Тень
    shadow = Image.new(
        "RGBA",
        (product.width + 80, 80),
        (0, 0, 0, 0)
    )

    shadow_draw = ImageDraw.Draw(shadow)

    shadow_draw.ellipse(
        (0, 20, product.width + 80, 70),
        fill=(0, 0, 0, 40)
    )

    card.paste(
        shadow,
        (px - 40, py + product.height - 10),
        shadow
    )

    card.paste(
        product,
        (px, py),
        product
    )

    # Блоки преимуществ
    start_y = 760

    block_colors = [
        (228, 240, 255),
        (230, 248, 235),
        (255, 244, 225)
    ]

    for i, block in enumerate(blocks[:3]):

        y1 = start_y + i * 120

        draw.rounded_rectangle(
            (60, y1, 840, y1 + 92),
            radius=26,
            fill=block_colors[i]
        )

        draw.text(
            (90, y1 + 28),
            f"✓ {block}",
            font=block_font,
            fill=(20, 30, 40)
        )

    # Нижний premium блок
    draw.rounded_rectangle(
        (60, 1110, 840, 1165),
        radius=24,
        fill=(10, 25, 45)
    )

    draw.text(
        (160, 1125),
        "Надёжность • Качество • Премиум",
        font=small_font,
        fill=(255, 255, 255)
    )

    output = BytesIO()

    card.save(
        output,
        format="PNG"
    )

    output.seek(0)

    return output.getvalue()


@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "🔥 WB Infocard AI Bot\n\n"
        "Отправь фото товара с подписью — я создам инфокарточку WB 900×1200 PNG."
    )


@dp.message(F.photo)
async def handle_photo(message: Message):

    caption = message.caption or "Товар для Wildberries"

    await message.answer(
        "🖼 Создаю инфокарточку..."
    )

    prompt = f"""
Ты эксперт по Wildberries.

Создай текст для первой инфокарточки.

Товар:
{caption}

Ответ строго:

ЗАГОЛОВОК:
БЛОК1:
БЛОК2:
БЛОК3:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    title, blocks = parse_ai_text(response.text)

    photo = message.photo[-1]

    file = await bot.get_file(photo.file_id)

    photo_bytes = BytesIO()

    await bot.download_file(
        file.file_path,
        photo_bytes
    )

    photo_bytes.seek(0)

    image_bytes = create_infocard(
        photo_bytes.getvalue(),
        title,
        blocks
    )

    result = BufferedInputFile(
        image_bytes,
        filename="wb_infocard.png"
    )

    await message.answer_photo(
        result,
        caption="✅ Инфокарточка WB готова"
    )


@dp.message(F.text)
async def generate_text(message: Message):

    user_text = message.text

    await message.answer(
        "⌛ Генерирую WB-текст..."
    )

    prompt = f"""
Ты профессиональный эксперт по Wildberries.

Товар:
{user_text}

Сделай:

1. SEO-заголовок
2. 10 SEO-ключей
3. 7 преимуществ
4. Продающее описание
5. Текст для 5 слайдов
6. Kling AI prompt

Пиши мощно и профессионально.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    await message.answer(
        response.text[:4000]
    )


async def main():

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())