from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

categories = {
    "🏠 Квартиры": "kvartiry",
    "🏡 Дома": "doma", 
    "🏗️ Новостройки": "novostroyki",
    "🏞️ Земельные участки": "zemelnie_uchastki",
    "🏢 Коммерческая недвижимость": "commercy"
}

quarters = {
    "Студии": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/kvartiry/ctudii/",
    "Комнаты": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/kvartiry/komnaty/",
    "1-комнатные": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/kvartiry/odnokomnatnye/",
    "2-комнатные": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/kvartiry/dvukhkomnatnye/",
    "3-комнатные": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/kvartiry/3-komnatnye/",
    "4-комнатные": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/kvartiry/4-komnatnye/",
    "5+ комнат": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/kvartiry/5-komnat/"
}

houses = {
    "Дома бизнес-класс": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/doma/doma-biznes-klass/",
    "Дуплекс": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/doma/dupleks/",
    "Коттеджи": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/doma/kottedzhi/",
    "Таунхаус": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/doma/taunkhaus/",
    "Часть дома": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/doma/chast-doma/",
    "Дома эконом-класса": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/doma/doma-ekonom-klassa/"
}

newbuildings = {
    "Бизнес-класса": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/novostroyki/biznes-klassa/",
    "Новостройки эконом-класса": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/novostroyki/novostroyki-ekonom-klassa/"
}

# Земельные участки (без подпунктов)
land_plots = {
    "Земельные участки": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/zemelnye-uchastki/"
}

# Коммерческая недвижимость (без подпунктов)
commercial = {
    "Коммерческая недвижимость": "https://www.xn----htbkhfjn2e0c.xn--p1ai/katalog-nedvizhimosti/kommercheskaya-nedvizhimost/"
}
def make_main_keyboard():
    """Создает главную клавиатуру с типами недвижимости"""
    buttons = []
    for name, callback_data in categories.items():
        buttons.append([InlineKeyboardButton(
            text=name, 
            callback_data=f"cat_{callback_data}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def make_subcategory_keyboard(subcategories_dict, back_button=True):
    """Создает клавиатуру подкатегорий"""
    buttons = []
    for name, url in subcategories_dict.items():
        buttons.append([InlineKeyboardButton(
            text=name,
            callback_data=f"sub_{name}"
        )])
    
    # Кнопка "Назад"
    if back_button:
        buttons.append([InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="back_to_main"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def make_property_keyboard(property_link):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Подробнее на сайте", url=property_link)]
    ])
    
def make_keyboard():
    return 