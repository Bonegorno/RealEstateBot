from bs4 import BeautifulSoup
from urllib.parse import urljoin
import aiohttp
import logging
import re

URL = "https://www.xn----htbkhfjn2e0c.xn--p1ai/"

def fix_url(url):
    """Исправляет URL, делая его абсолютным"""
    if url.startswith('/'):
        return urljoin(URL, url)
    return url

async def fetch_properties(category_url):
    """Парсит карточки недвижимости с сайта"""
    try:
        url = fix_url(category_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    properties = []
                    property_cards = soup.find_all('div', class_='catalog-page-cart__item')
                    
                    for card in property_cards[:5]:
                        property_data = {}
                        
                        # Название
                        title_elem = card.find(['a'], class_='catalog-page-cart__title')
                        property_data['title'] = title_elem.get_text(strip=True) if title_elem else "Название не указано"
                        
                        # Цена
                        all_prices = []
                        
                        # Ищем ВСЕ элементы с ценами
                        main_prices = card.find_all(class_='catalog-page-cart__prices')
                        for price_elem in main_prices:
                            price_text = price_elem.get_text(strip=True)
                            if price_text:
                                all_prices.append(price_text)
                        
                        alt_prices = card.find_all(class_='catalog-page-cart__prices-alt')
                        for price_elem in alt_prices:
                            price_text = price_elem.get_text(strip=True)
                            if price_text:
                                all_prices.append(price_text)
                        
                        if not all_prices:
                            any_prices = card.find_all(class_=re.compile(r'catalog-page-cart__prices|catalog-page-cart__prices-alt'))
                            for price_elem in any_prices:
                                price_text = price_elem.get_text(strip=True)
                                if price_text:
                                    all_prices.append(price_text)
                        
                        # Объединяем все найденные цены с переносом строки
                        if all_prices:
                            property_data['price'] = '\n'.join(all_prices)
                        else:
                            property_data['price'] = "Цена не указана"
                        
                        # Фото
                        img_elem = card.find('img')
                        if img_elem:
                            img_src = img_elem.get('src') or img_elem.get('data-src')
                            property_data['image'] = fix_url(img_src) if img_src else None
                        else:
                            property_data['image'] = None
                        
                        # Ссылка на объект
                        link_elem = card.find('a', 'catalog-page-cart__title', href=True)
                        if link_elem:
                            href = link_elem.get('href')
                            property_data['link'] = fix_url(href)
                        else:
                            # Если не нашли в заголовке, ищем любую ссылку в карточке
                            any_link_elem = card.find('a', href=True)
                            if any_link_elem:
                                href = any_link_elem.get('href')
                                property_data['link'] = fix_url(href)
                            else:
                                property_data['link'] = url
                        
                        if property_data['title'] != "Название не указано":
                            properties.append(property_data)
                    
                    return properties
                else:
                    return []
    except Exception as e:
        logging.error(f"Ошибка при парсинге: {e}")
        return []