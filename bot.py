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
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
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
        if bbox[2] <= max_width:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "

    if line:
        lines.append(line.strip())

    return lines


def parse_ai_text(text):
    title = "Премиум товар для WB"
    blocks = ["Качественные материалы", "Надёжная конструкция", "Готов к установке"]

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

    card = Image.new("RGB", (W, H), (245, 248, 250))
    draw = ImageDraw.Draw(card)

    # Фон
    draw.rounded_rectangle((35, 35, 865, 1165), radius=40, fill=(255, 255, 255))
    draw.rounded_rectangle((55, 55, 845, 205), radius=32, fill=(20, 28, 38))

    title_font = get_font(48, bold=True)
    text_font = get_font(30, bold=False)
    block_font = get_font(31, bold=True)
    small_font = get_font(24, bold=False)

    # Заголовок
    y = 78
    for line in wrap_text(draw, title, title_font, 750):
        draw.text((85, y), line, font=title_font, fill=(255, 255, 255))
        y += 56

    draw.text((85, 175), "Для Wildberries • 900×1200", font=small_font, fill=(190, 210, 230))

    # Фото товара
    product = Image.open(BytesIO(product_bytes)).convert("RGBA")
    product.thumbnail((760, 500), Image.LANCZOS)

    px = (W - product.width) // 2
    py = 260

    shadow = Image.new("RGBA", product.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse((40, product.height - 45, product.width - 40, product.height - 5), fill=(0, 0, 0, 45))
    card.paste(shadow, (px, py + 35), shadow)

    card.paste(product, (px, py), product)

    # Блоки преимуществ
    block_y = 790
    colors = [(232, 245, 255), (235, 255, 242), (255, 247, 230)]

    for i, block in enumerate(blocks[:3]):
        y1 = block_y + i * 115
        draw.rounded_rectangle((70, y1, 830, y1 + 88), radius=24, fill=colors[i], outline=(220, 225, 230), width=2)
        draw.text((100, y1 + 24), f"✓ {block}", font=block_font, fill=(25, 35, 45))

    # Нижний призыв
    draw.rounded_rectangle((70, 1130, 830, 1180), radius=22, fill=(20, 28, 38))
    draw.text((145, 1142), "Премиум качество • готово к продаже", font=text_font, fill=(255, 255, 255))

    output = BytesIO()
    card.save(output, format="PNG")
    output.seek(0)

    return output.getvalue()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🔥 WB Infocard AI Bot\n\n"
        "Отправь фото товара с подписью — я создам первую PNG-инфокарточку 900×1200.\n\n"
        "Также можно отправить название товара текстом — я сделаю SEO и описание."
    )


@dp.message(F.photo)
async def handle_photo(message: Message):
    caption = message.caption or "Товар для Wildberries"

    await message.answer("🖼 Создаю инфокарточку WB 900×1200...")

    prompt = f"""
Ты эксперт по инфокарточкам Wildberries.

По товару составь короткий текст для первой инфокарточки.

Товар: {caption}

Ответ строго в формате:
ЗАГОЛОВОК: короткий продающий заголовок до 45 символов
БЛОК1: преимущество до 28 символов
БЛОК2: преимущество до 28 символов
БЛОК3: преимущество до 28 символов

Без лишнего текста.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    title, blocks = parse_ai_text(response.text)

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)

    photo_bytes = BytesIO()
    await bot.download_file(file.file_path, photo_bytes)
    photo_bytes.seek(0)

    image_bytes = create_infocard(photo_bytes.getvalue(), title, blocks)

    result = BufferedInputFile(
        image_bytes,
        filename="wb_infocard_900x1200.png"
    )

    await message.answer_photo(result, caption="✅ Готово: инфокарточка WB 900×1200 PNG")


@dp.message(F.text)
async def generate_text(message: Message):
    user_text = message.text

    await message.answer("⌛ Генерирую WB-текст...")

    prompt = f"""
Ты профессиональный эксперт по Wildberries, инфокарточкам WB, SEO-продажам и маркетингу.

Товар: {user_text}

Сделай:
1. SEO-заголовок WB до 60 символов
2. 10 SEO-ключей через запятую
3. 7 преимуществ товара
4. Продающее описание товара
5. Текст для 5 слайдов инфокарточки
6. Kling AI prompt для видео 9:16

Пиши мощно, без воды, в стиле ТОП-карточек WB.
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