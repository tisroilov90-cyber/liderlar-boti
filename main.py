import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# TAYYOR SOZLAMALAR
ADMIN_ID = 5028334030 
TOKEN = "8750166767:AAH6VUZ1ma6vbemGKEHEmBZwMWPKCnIyQcQ" 
CHANNEL_USERNAME = "@kelajak_liderlari_43" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

class AdminForm(StatesGroup):
    edit_id = State()
    full_name = State()
    phone = State()
    tg_link = State()

def init_db():
    conn = sqlite3.connect('liderlar.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            direction TEXT,
            full_name TEXT,
            phone TEXT,
            telegram_link TEXT
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM leaders')
    if cursor.fetchone()[0] == 0:
        directions = [
            "👑 Kelajak Lideri", "📚 Ta'lim yo'nalishi", "🎭 Madaniyat yo'nalishi", 
            "💻 IT va sun'iy intellekt", "⚽️ Sport yo'nalishi", 
            "🌱 Ekologiya yo'nalishi", "📸 Media yo'nalishi", 
            "🤝 Ijtimoiy tashabbus", "🏢 MMIBDO (Zavuch)"
        ]
        for dir_name in directions:
            cursor.execute('INSERT INTO leaders (direction, full_name, phone, telegram_link) VALUES (?, ?, ?, ?)', 
                           (dir_name, "Hali kiritilmagan", "+998000000000", "https://t.me/"))
        conn.commit()
    conn.close()

init_db()

# --- MENYULAR ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Kelajak liderlari bilan bog'lanish")],
        [KeyboardButton(text="🏢 Maktab ma'muriyati (MMIBDO) bilan bog'lanish")]
    ], resize_keyboard=True, input_field_placeholder="Quyidagi menyulardan birini tanlang"
)

liderlar_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👑 Kelajak Lideri", callback_data="lider_1")],
        [InlineKeyboardButton(text="📚 Ta'lim", callback_data="lider_2"), InlineKeyboardButton(text="🎭 Madaniyat", callback_data="lider_3")],
        [InlineKeyboardButton(text="💻 IT va AI", callback_data="lider_4"), InlineKeyboardButton(text="⚽️ Sport", callback_data="lider_5")],
        [InlineKeyboardButton(text="🌱 Ekologiya", callback_data="lider_6"), InlineKeyboardButton(text="📸 Media", callback_data="lider_7")],
        [InlineKeyboardButton(text="🤝 Ijtimoiy tashabbus", callback_data="lider_8")]
    ]
)

admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👑 Kelajak Lideri", callback_data="edit_1")],
        [InlineKeyboardButton(text="📚 Ta'lim", callback_data="edit_2"), InlineKeyboardButton(text="🎭 Madaniyat", callback_data="edit_3")],
        [InlineKeyboardButton(text="💻 IT va AI", callback_data="edit_4"), InlineKeyboardButton(text="⚽️ Sport", callback_data="edit_5")],
        [InlineKeyboardButton(text="🌱 Ekologiya", callback_data="edit_6"), InlineKeyboardButton(text="📸 Media", callback_data="edit_7")],
        [InlineKeyboardButton(text="🤝 Ijtimoiy tashabbus", callback_data="edit_8")],
        [InlineKeyboardButton(text="🏢 MMIBDO (Zavuch)", callback_data="edit_9")]
    ]
)

# --- OBUNA TEKSHIRISH ---
async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except TelegramBadRequest:
        return False

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    is_subscribed = await check_sub(message.from_user.id)
    if is_subscribed:
        await message.answer(f"Assalomu alaykum, {message.from_user.first_name}!\nBosh menyudasiz.", reply_markup=main_menu)
    else:
        sub_menu = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription")]
        ])
        await message.answer("Botdan foydalanish uchun kanalimizga obuna bo'ling!", reply_markup=sub_menu)

@dp.callback_query(F.data == "check_subscription")
async def check_btn_handler(callback: types.CallbackQuery):
    if await check_sub(callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer("Obunangiz tasdiqlandi!", reply_markup=main_menu)
    else:
        await callback.answer("Hali kanalga obuna bo'lmapsiz!", show_alert=True)

# --- LIDERLAR MA'LUMOTI ---
@dp.message(F.text == "👥 Kelajak liderlari bilan bog'lanish")
async def show_leaders(message: types.Message):
    await message.answer("Qaysi yo'nalish koordinatori bilan bog'lanmoqchisiz?", reply_markup=liderlar_menu)

@dp.callback_query(F.data.startswith("lider_"))
async def show_leader_info(callback: types.CallbackQuery):
    lider_id = int(callback.data.split("_")[1])
    conn = sqlite3.connect('liderlar.db')
    cursor = conn.cursor()
    cursor.execute('SELECT direction, full_name, phone, telegram_link FROM leaders WHERE id = ?', (lider_id,))
    data = cursor.fetchone()
    conn.close()
    
    if data:
        direction, full_name, phone, tg_link = data
        info_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Telegram orqali yozish", url=tg_link)]
        ])
        await callback.message.edit_text(f"🔹 **{direction}**\n\n👤 Ism-familiya: {full_name}\n📞 Raqam: {phone}", reply_markup=info_btn, parse_mode="Markdown")

@dp.message(F.text == "🏢 Maktab ma'muriyati (MMIBDO) bilan bog'lanish")
async def show_zavuch(message: types.Message):
    conn = sqlite3.connect('liderlar.db')
    cursor = conn.cursor()
    cursor.execute('SELECT full_name, phone, telegram_link FROM leaders WHERE id = 9')
    data = cursor.fetchone()
    conn.close()
    
    if data:
        full_name, phone, tg_link = data
        info_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Telegram orqali yozish", url=tg_link)]
        ])
        await message.answer(f"🏢 **MMIBDO (Zavuch)**\n\n👤 Ism-familiya: {full_name}\n📞 Raqam: {phone}", reply_markup=info_btn, parse_mode="Markdown")

# --- ADMIN PANEL ---
@dp.message(Command("admin"))
async def admin_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("👨‍💻 **Admin panelga xush kelibsiz!**\nMa'lumotlarini o'zgartirmoqchi bo'lganingizni tanlang:", reply_markup=admin_menu)

@dp.callback_query(F.data.startswith("edit_"))
async def edit_leader_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    lider_id = int(callback.data.split("_")[1])
    await state.update_data(edit_id=lider_id)
    await callback.message.answer("✏️ Liderning **Ism-Familiyasini** kiriting:")
    await state.set_state(AdminForm.full_name)

@dp.message(AdminForm.full_name)
async def edit_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("📞 Endi uning **Telefon raqamini** kiriting:")
    await state.set_state(AdminForm.phone)

@dp.message(AdminForm.phone)
async def edit_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("💬 Endi uning **Telegram profilini** kiriting:")
    await state.set_state(AdminForm.tg_link)

@dp.message(AdminForm.tg_link)
async def edit_tg_link(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    edit_id = user_data['edit_id']
    full_name = user_data['full_name']
    phone = user_data['phone']
    
    # AVTOMATIK TO'G'RILASH QISMI (Xatolikni oldini oladi)
    tg_link = message.text.strip()
    if tg_link.startswith("@"):
        tg_link = f"https://t.me/{tg_link[1:]}"
    elif not tg_link.startswith("http"):
        tg_link = f"https://t.me/{tg_link}"
    
    conn = sqlite3.connect('liderlar.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE leaders SET full_name = ?, phone = ?, telegram_link = ? WHERE id = ?''', 
                   (full_name, phone, tg_link, edit_id))
    conn.commit()
    conn.close()
    
    await message.answer(f"✅ Ma'lumotlar saqlandi!\n👤 {full_name}\n📞 {phone}\n🔗 {tg_link}\n\nEndi oddiy menyudan tekshirib ko'rishingiz mumkin.")
    await state.clear()

async def main():
    print("Bot ishlashni boshladi! Admin panel avtomatik to'g'rilash bilan ulandi.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())