from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from keyboards import make_subcategory_keyboard, quarters, houses, newbuildings, land_plots, commercial, make_main_keyboard, make_property_keyboard
from textformat import format_property_message, format_property_message_html
import asyncio
import logging
from parse_cards import fix_url, fetch_properties

category_router = Router()

@category_router.callback_query(F.data == "back_to_main")
async def back_to_main_handler(call: CallbackQuery):
    kb = make_main_keyboard()
    await call.message.edit_text(
        "🏘️ Добро пожаловать в бот недвижимости!\n"
        "Выберите тип недвижимости:",
        reply_markup=kb
    )
    await call.answer()

@category_router.callback_query(F.data.startswith("cat_"))
async def category_handler(call: CallbackQuery):
    category_type = call.data.replace("cat_", "")
    
    if category_type == "kvartiry":
        kb = make_subcategory_keyboard(quarters)
        await call.message.edit_text(
        "🏠 Выберите тип квартир:",
        reply_markup=kb
        )
    
    elif category_type == "doma":
        kb = make_subcategory_keyboard(houses)
        await call.message.edit_text(
        "🏡 Выберите тип домов:",
        reply_markup=kb
        )
    
    elif category_type == "novostroyki":
        kb = make_subcategory_keyboard(newbuildings)
        await call.message.edit_text(
        "🏗️ Выберите тип новостроек:",
        reply_markup=kb
        )
    
    elif category_type == "zemelnie_uchastki":
        kb = make_subcategory_keyboard(land_plots)
        await call.message.edit_text(
        "🏞️ Земельные участки:",
        reply_markup=kb
        )
    
    elif category_type == "commercy":
        kb = make_subcategory_keyboard(commercial)
        await call.message.edit_text(
        "🏢 Коммерческая недвижимость:",
        reply_markup=kb
        )
    
    await call.answer()

@category_router.callback_query(F.data.startswith("sub_"))
async def subcategory_handler(call: CallbackQuery):
    """Обработчик выбора подкатегории"""
    subcategory_name = call.data.replace("sub_", "")
    
    # Определяем URL в зависимости от подкатегории
    url = None
    
    if subcategory_name in quarters:
        url = quarters[subcategory_name]
    elif subcategory_name in houses:
        url = houses[subcategory_name]
    elif subcategory_name in newbuildings:
        url = newbuildings[subcategory_name]
    elif subcategory_name in land_plots:
        url = land_plots[subcategory_name]
    elif subcategory_name in commercial:
        url = commercial[subcategory_name]

    
    if not url:
        await call.answer("Категория не найдена", show_alert=True)
        return
    
    await call.message.edit_text(f"🔍 Ищу актуальные предложения ({subcategory_name})...")
    
    # Парсим свойства
    properties = await fetch_properties(url)
    
    if not properties:
        await call.message.answer(
            f"Не удалось загрузить данные для категории '{subcategory_name}'. "
            f"Вот ссылка на раздел: {fix_url(url)}"
        )
        await call.answer()
        return
    
    # Отправляем карточки
    sent_count = 0
    for prop in properties[:3]:
        try:
            
            message_text = format_property_message(prop, subcategory_name)
            property_keyboard = make_property_keyboard(prop['link'])
            
            # Добавим отладочную информацию
            logging.info(f"Отправка карточки {prop['title']} | Ссылка: {prop['link']}")
            
            if prop.get('image'):
                await call.message.answer_photo(
                    photo=prop['image'],
                    caption=message_text,
                    reply_markup=property_keyboard,
                    parse_mode='MarkdownV2'
                )
            else:
                await call.message.answer(
                    message_text,
                    reply_markup=property_keyboard,
                    parse_mode='HTML'
                )
            
            sent_count += 1
            await asyncio.sleep(1)
            
        except Exception as e:
            logging.error(f"Ошибка при отправке карточки: {e}")
            try:
                await call.message.answer(
                    format_property_message(prop),
                    reply_markup=make_property_keyboard(prop['link']),
                    parse_mode='HTML'
                )
                sent_count += 1
            except Exception as e2:
                logging.error(f"Не удалось отправить даже текстовую версию: {e2}")
    
    if sent_count == 0:
        await call.message.answer(
            f"Не удалось загрузить карточки для категории '{subcategory_name}'. "
            f"Вот ссылка на раздел: {fix_url(url)}"
        )
    
    # Добавляем кнопку для возврата
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад к категориям", callback_data="back_to_main")]
    ])
    await call.message.answer("Выберите следующее действие:", reply_markup=back_kb)
    
    await call.answer()