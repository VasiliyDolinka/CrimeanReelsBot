import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
import smtplib
from email.message import EmailMessage

# Твои данные
BOT_TOKEN = "7753772066:AAG9KTQsz-XrF5vL_37iYN9GZT5xbFq72Lw"
GMAIL_USER = "Dolinkavasya@gmail.com"
GMAIL_PASS = "ryhjddfntifhnmha"
GROUP_CHAT_ID = -1002126781384

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    business = State()
    task = State()
    budget = State()
    name = State()
    phone = State()

async def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_USER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.send_message(msg)

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(
        "👋 Привет! Я помогу тебе создать 🎞 Reels для твоего бизнеса 📈\n\n"
        "Напиши, пожалуйста, какое у тебя направление деятельности 👇"
    )
    await state.set_state(Form.business)

@dp.message(Form.business)
async def process_business(message: Message, state: FSMContext):
    await state.update_data(business=message.text)
    await message.answer("✍️ Отлично! Теперь расскажи, какую задачу ты хочешь решить с помощью Reels?")
    await state.set_state(Form.task)

@dp.message(Form.task)
async def process_task(message: Message, state: FSMContext):
    await state.update_data(task=message.text)
    await message.answer("💸 Какой примерный бюджет на съёмку?")
    await state.set_state(Form.budget)

@dp.message(Form.budget)
async def process_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("👤 Как тебя зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 И оставь, пожалуйста, свой номер телефона:")
    await state.set_state(Form.phone)

@dp.message(Form.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()

    text = (
        f"📥 Новая заявка от @{message.from_user.username or message.from_user.full_name}\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"📌 Направление: {data['business']}\n"
        f"🛠 Задача: {data['task']}\n"
        f"💰 Бюджет: {data['budget']}"
    )

    try:
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
    except:
        pass

    await send_email("Новая заявка от Telegram-бота", text)
    await message.answer("Спасибо большое за заявку! Хорошего вам дня ☀️")
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())