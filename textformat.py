def escape_markdown(text):
    """Экранирует специальные символы для MarkdownV2"""
    if not text:
        return ""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in text])

def format_property_message(property_data, category_name):
    """Форматирует сообщение для карточки недвижимости"""
    title = escape_markdown(property_data['title'])
    price = escape_markdown(property_data['price'])
    link = property_data['link']
    
    # Для MarkdownV2 ссылки: [текст](URL)
    return (
        f"🏠 {title}\n\n"
        f"💰 {price}\n\n"
    )

def format_property_message_html(property_data, category_name):
    """Форматирует сообщение для карточки недвижимости с HTML (для текстовых сообщений)"""
    return (
        f"🏠 {property_data['title']}\n\n"
        f"💰 {property_data['price']}\n\n"
    )