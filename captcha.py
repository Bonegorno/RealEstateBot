from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import make_main_keyboard
import random
from datetime import datetime, timedelta

start_router = Router()

class CaptchaStates(StatesGroup):
    waiting_for_captcha = State()

# Ключи в FSM
BAN_UNTIL = "ban_until"      # datetime.isoformat()
CAPTCHA_ANS = "captcha_ans"  # правильный ответ
ATTEMPTS = "attempts"        # счетчик попыток
PASSED = "passed"            # флаг прохождения

def generate_captcha():
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    return a, b, a + b, f"{a} + {b} = ?"

def make_captcha_kb(user_id: int, correct: int):
    options = [
        correct,
        correct + random.randint(1, 10),
        max(0, correct - random.randint(1, 10)),
        correct + random.randint(5, 15)
    ]
    random.shuffle(options)
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    row = []
    for opt in options:
        row.append(InlineKeyboardButton(text=str(opt), callback_data=f"cap:{user_id}:{opt}"))
        if len(row) == 2:
            kb.inline_keyboard.append(row)
            row = []
    if row:
        kb.inline_keyboard.append(row)
    return kb

async def check_ban(state: FSMContext) -> tuple[bool, str | None]:
    data = await state.get_data()
    ban_str = data.get(BAN_UNTIL)
    if not ban_str:
        return False, None
    try:
        ban_until = datetime.fromisoformat(ban_str)
        if datetime.now() < ban_until:
            left = int((ban_until - datetime.now()).total_seconds())
            m, s = divmod(left, 60)
            txt = f"{m} мин {s} сек" if m else f"{s} сек"
            return True, txt
    except:
        pass
    return False, None

async def send_new_captcha(message_obj: Message | CallbackQuery, state: FSMContext, user_id: int):
    """Выдает новую капчу, сохраняя текущие попытки"""
    _, _, correct, question = generate_captcha()
    
    # Сохраняем текущие данные, только обновляем CAPTCHA_ANS
    current_data = await state.get_data()
    current_data[CAPTCHA_ANS] = correct
    await state.set_data(current_data)
    
    kb = make_captcha_kb(user_id, correct)

    text = f"Неверно! Осталась 1 попытка.\n\n{question}"
    if isinstance(message_obj, Message):
        await message_obj.answer(text, reply_markup=kb)
    else:
        await message_obj.message.edit_text(text, reply_markup=kb)

@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()

    # 1. Уже прошёл капчу навсегда?
    if data.get(PASSED):
        await message.answer("Ты уже прошёл проверку ✅", reply_markup=make_main_keyboard())
        return

    # 2. В бане?
    banned, time_left = await check_ban(state)
    if banned:
        await message.answer(
            f"Ты заблокирован за ошибки.\n"
            f"Осталось: {time_left}\n"
            f"Перезапуск /start не поможет — жди."
        )
        return

    # 3. Нормальная выдача капчи
    _, _, correct, question = generate_captcha()
    await state.set_data({
        CAPTCHA_ANS: correct,
        ATTEMPTS: 0,
        PASSED: False  # явно указываем флаг
    })
    kb = make_captcha_kb(user_id, correct)

    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n"
        "Пройди проверку:\n\n"
        f"{question}",
        reply_markup=kb
    )

@start_router.callback_query(F.data.startswith("cap:"))
async def process_captcha(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    try:
        _, uid_str, ans_str = callback.data.split(":")
        uid, answer = int(uid_str), int(ans_str)
    except:
        return

    if uid != user_id:
        return await callback.answer("Не твоя капча!", show_alert=True)

    # Проверка бана
    banned, time_left = await check_ban(state)
    if banned:
        await callback.message.edit_text(
            f"Ты в бане.\nОсталось: {time_left}\nПерезапуск не поможет.",
            reply_markup=None
        )
        return await callback.answer("Заблокирован", show_alert=True)

    data = await state.get_data()
    
    # Проверяем, не прошел ли уже пользователь капчу
    if data.get(PASSED):
        await callback.message.edit_text("Проверка уже пройдена! ✅", reply_markup=None)
        await callback.message.answer(
            "Выберите тип недвижимости:",
            reply_markup=make_main_keyboard()
        )
        return await callback.answer("Уже пройдено!")

    correct = data.get(CAPTCHA_ANS)
    attempts = data.get(ATTEMPTS, 0)

    # ПРАВИЛЬНЫЙ ОТВЕТ
    if answer == correct:
        await state.update_data({PASSED: True})   # ← устанавливаем флаг прохождения

        await callback.message.edit_text("Проверка пройдена! Добро пожаловать! ✅", reply_markup=None)
        await callback.message.answer(
            "Выберите тип недвижимости:",
            reply_markup=make_main_keyboard()
        )
        await callback.answer("Верно!")
        return

    # НЕПРАВИЛЬНЫЙ ОТВЕТ
    attempts += 1
    await state.update_data({ATTEMPTS: attempts})  # ← обновляем счетчик попыток

    if attempts >= 2:
        # БАН НА 2 МИНУТЫ
        ban_until = datetime.now() + timedelta(minutes=2)
        await state.update_data({BAN_UNTIL: ban_until.isoformat()})

        await callback.message.edit_text(
            "Две ошибки подряд!\n\n"
            "Заблокирован на 2 минуты.\n"
            "Перезапуск /start не поможет — просто подожди.",
            reply_markup=None
        )
        await callback.answer("Заблокирован на 2 минуты", show_alert=True)
    else:
        # Одна ошибка — даём последнюю попытку
        await send_new_captcha(callback, state, user_id)
        await callback.answer("Неверно!")