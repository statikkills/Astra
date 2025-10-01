import requests
from bs4 import BeautifulSoup
import re
import webbrowser
import os
import sys
import subprocess
from colorama import init, Fore, Back, Style
from urllib.parse import urlparse
import time
from pystyle import Colors, Colorate, Write, Center, Box
import phonenumbers
from phonenumbers import carrier, geocoder
import json

init(autoreset=True)

WEB_API_URL = "https://htmlweb.ru/geo/api.php?json&telcod="

def install_libraries():
    libraries = ['requests', 'bs4', 'colorama', 'urllib3', 'pystyle', 'phonenumbers']
    for lib in libraries:
        try:
            __import__(lib)
        except ImportError:
            print(f"{Fore.MAGENTA}Установка {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

def get_web_data(phone_number):
    """Получает дополнительные данные о номере из внешнего API"""
    try:
        clean_number = phone_number.replace("+", "")

        response = requests.get(
            f"{WEB_API_URL}{clean_number}",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

class PhoneAnalyzer:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.results = {
            "basic_info": {},
            "web_info": {}
        }
        self.parsed_number = None

    def validate_and_parse(self):
        """Валидация и базовый анализ номера"""
        try:
            cleaned_number = re.sub(r'[^\d+]', '', self.phone_number)

            if cleaned_number.startswith('8') and len(cleaned_number) == 11:
                cleaned_number = '+7' + cleaned_number[1:]

            self.parsed_number = phonenumbers.parse(cleaned_number, None)

            if not phonenumbers.is_valid_number(self.parsed_number):
                return False

            country = geocoder.description_for_number(self.parsed_number, "ru")
            operator = carrier.name_for_number(self.parsed_number, "ru")

            self.results["basic_info"] = {
                "is_valid": True,
                "country": country,
                "operator": operator,
                "national_format": phonenumbers.format_number(
                    self.parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL
                ),
                "international_format": phonenumbers.format_number(
                    self.parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                ),
                "e164_format": phonenumbers.format_number(
                    self.parsed_number, phonenumbers.PhoneNumberFormat.E164
                )
            }
            return True
        except:
            return False

    def check_web_info(self):
        """Получает дополнительную информацию из внешнего API"""
        web_data = get_web_data(self.phone_number)
        if web_data:
            self.results["web_info"] = {
                "postal": web_data.get("0", {}).get("post", "Неизвестно"),
                "region": web_data.get("region", {}).get("name", "Неизвестно"),
                "autocod": web_data.get("region", {}).get("autocod", "Неизвестно"),
                "operator": web_data.get("0", {}).get("oper", "Неизвестно"),
                "brand": web_data.get("0", {}).get("oper_brand", "Неизвестно"),
                "latitude": web_data.get("0", {}).get("latitude", "Неизвестно"),
                "longitude": web_data.get("0", {}).get("longitude", "Неизвестно"),
                "capital": web_data.get("capital", {}).get("name", "Неизвестно"),
                "country": web_data.get("country", {}).get("name", "Неизвестно")
            }
            return True
        return False

    def run_analysis(self):
        """Запуск полного анализа"""
        if not self.validate_and_parse():
            return False

        self.check_web_info()

        return True

def display_phone_results(results):
    """Отображает результаты анализа в консоли"""
    basic = results["basic_info"]
    web_info = results.get("web_info", {})

    Write.Print("\n" + "═" * 60 + "\n", Colors.purple_to_blue, interval=0.01)
    Write.Print("📱 АНАЛИЗ НОМЕРА ТЕЛЕФОНА\n", Colors.purple_to_blue, interval=0.01)
    Write.Print("═" * 60 + "\n", Colors.purple_to_blue, interval=0.01)
    
    Write.Print("ОСНОВНАЯ ИНФОРМАЦИЯ:\n", Colors.blue_to_purple, interval=0.01)
    print(Colorate.Horizontal(Colors.purple_to_blue, f"• Номер: {basic.get('international_format', 'N/A')}", 1))
    print(Colorate.Horizontal(Colors.purple_to_blue, f"• Локальный формат: {basic.get('national_format', 'N/A')}", 1))
    print(Colorate.Horizontal(Colors.purple_to_blue, f"• Страна: {basic.get('country', 'N/A')}", 1))
    print(Colorate.Horizontal(Colors.purple_to_blue, f"• Оператор: {basic.get('operator', 'N/A')}", 1))
    print(Colorate.Horizontal(Colors.purple_to_blue, f"• Валидный: {'Да' if basic.get('is_valid') else 'Нет'}", 1))

    if web_info:
        Write.Print("\nДЕТАЛЬНАЯ ИНФОРМАЦИЯ (htmlweb.ru):\n", Colors.blue_to_purple, interval=0.01)
        
        if web_info.get('region') != "Неизвестно":
            print(Colorate.Horizontal(Colors.purple_to_blue, f"• Регион: {web_info['region']}", 1))
        
        if web_info.get('postal') != "Неизвестно":
            print(Colorate.Horizontal(Colors.purple_to_blue, f"• Почтовый индекс: {web_info['postal']}", 1))
        
        if web_info.get('autocod') != "Неизвестно":
            print(Colorate.Horizontal(Colors.purple_to_blue, f"• Автономер региона: {web_info['autocod']}", 1))
        
        if web_info.get('operator') != "Неизвестно":
            print(Colorate.Horizontal(Colors.purple_to_blue, f"• Оператор: {web_info['operator']}", 1))
        
        if web_info.get('brand') != "Неизвестно":
            print(Colorate.Horizontal(Colors.purple_to_blue, f"• Бренд: {web_info['brand']}", 1))
        
        if web_info.get('latitude') != "Неизвестно" and web_info.get('longitude') != "Неизвестно":
            print(Colorate.Horizontal(Colors.purple_to_blue, f"• Координаты: {web_info['latitude']}, {web_info['longitude']}", 1))
            maps_url = f"https://www.google.com/maps?q={web_info['latitude']},{web_info['longitude']}"
            print(Colorate.Horizontal(Colors.blue_to_purple, f"• Ссылка на карты: {maps_url}", 1))
        
        if web_info.get('capital') != "Неизвестно":
            print(Colorate.Horizontal(Colors.purple_to_blue, f"• Столица: {web_info['capital']}", 1))
        
        if web_info.get('country') != "Неизвестно":
            print(Colorate.Horizontal(Colors.purple_to_blue, f"• Страна: {web_info['country']}", 1))

    Write.Print("\nПОЛЕЗНЫЕ ССЫЛКИ:\n", Colors.blue_to_purple, interval=0.01)
    e164_clean = basic.get('e164_format', '').replace('+', '')
    print(Colorate.Horizontal(Colors.purple_to_blue, f"• WhatsApp: https://wa.me/{e164_clean}", 1))
    print(Colorate.Horizontal(Colors.purple_to_blue, f"• Viber: https://viber.click/{e164_clean}", 1))
    print(Colorate.Horizontal(Colors.purple_to_blue, f"• Telegram: https://t.me/{e164_clean}", 1))
    
    Write.Print("\n" + "═" * 60 + "\n", Colors.purple_to_blue, interval=0.01)

def search_phone_number(phone_number):
    url = "https://www.google.com/search?q={}".format(phone_number)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('a', href=True)
        
        excluded_domains = ['google.com', 'yandex.ru', 'bing.com', 'maps.google.com']
        
        unique_links = set()
        
        for link in search_results:
            href = link.get('href', '')
            match = re.search(r'(https?://[^&]+)', href)
            if match:
                url = match.group(1)
                parsed_url = urlparse(url)
                if not any(domain in parsed_url.netloc for domain in excluded_domains):
                    unique_links.add(url)
        
        return list(unique_links)
        
    except requests.RequestException as e:
        return f"Ошибка при выполнении запроса: {str(e)}"

def save_links_to_html(links, phone_number, analysis_results, filename="search_results.html"):
    css_styles = """
        <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
            background: linear-gradient(135deg, #2d1b69 0%, #1a1033 100%);
            color: #e6e6fa;
            min-height: 100vh;
        }
        .container { 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 40px 20px;
        }
        h1 { 
            text-align: center; 
            margin-bottom: 30px; 
            font-size: 2.5em; 
            color: #b19cd9;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        .phone-info {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(177, 156, 217, 0.1);
            border-radius: 8px;
            border: 1px solid #9370db;
        }
        .analysis-section {
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(177, 156, 217, 0.05);
            border-radius: 8px;
            border: 1px solid #9370db;
        }
        .analysis-section h3 {
            color: #b19cd9;
            margin-bottom: 15px;
        }
        .analysis-item {
            margin-bottom: 8px;
            padding: 5px 0;
        }
        .stats {
            text-align: center;
            margin-bottom: 20px;
            font-size: 1.1em;
            color: #d8bfd8;
        }
        .link-list { 
            list-style-type: none; 
        }
        .link-item { 
            margin-bottom: 15px; 
            padding: 20px; 
            background: rgba(177, 156, 217, 0.1);
            border: 1px solid #9370db;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .link-item:hover { 
            transform: translateY(-3px);
            background: rgba(177, 156, 217, 0.2);
            box-shadow: 0 5px 15px rgba(147, 112, 219, 0.3);
        }
        .link-item a { 
            display: block; 
            color: #b19cd9; 
            text-decoration: none; 
            font-size: 1.1em;
            font-weight: 500;
            transition: color 0.3s ease;
        }
        .link-item a:hover { 
            color: #da70d6; 
        }
        .domain {
            font-size: 0.9em;
            color: #d8bfd8;
            margin-top: 5px;
        }
        .timestamp {
            text-align: center;
            margin-top: 30px;
            color: #9370db;
            font-style: italic;
        }
        </style>
    """

    analysis_html = ""
    if "basic_info" in analysis_results:
        basic = analysis_results["basic_info"]
        web_info = analysis_results.get("web_info", {})
        
        analysis_html = f"""
        <div class="analysis-section">
            <h3>📱 Анализ номера</h3>
            <div class="analysis-item"><strong>Номер:</strong> {basic.get('international_format', 'N/A')}</div>
            <div class="analysis-item"><strong>Страна:</strong> {basic.get('country', 'N/A')}</div>
            <div class="analysis-item"><strong>Оператор:</strong> {basic.get('operator', 'N/A')}</div>
            <div class="analysis-item"><strong>Валидный:</strong> {'Да' if basic.get('is_valid') else 'Нет'}</div>
        """
        
        if web_info:
            if web_info.get('region') != "Неизвестно":
                analysis_html += f'<div class="analysis-item"><strong>Регион:</strong> {web_info["region"]}</div>'
            
            if web_info.get('postal') != "Неизвестно":
                analysis_html += f'<div class="analysis-item"><strong>Почтовый индекс:</strong> {web_info["postal"]}</div>'
            
            if web_info.get('autocod') != "Неизвестно":
                analysis_html += f'<div class="analysis-item"><strong>Автономер региона:</strong> {web_info["autocod"]}</div>'
            
            if web_info.get('operator') != "Неизвестно":
                analysis_html += f'<div class="analysis-item"><strong>Оператор (API):</strong> {web_info["operator"]}</div>'
            
            if web_info.get('brand') != "Неизвестно":
                analysis_html += f'<div class="analysis-item"><strong>Бренд:</strong> {web_info["brand"]}</div>'
            
            if web_info.get('latitude') != "Неизвестно" and web_info.get('longitude') != "Неизвестно":
                analysis_html += f'<div class="analysis-item"><strong>Координаты:</strong> {web_info["latitude"]}, {web_info["longitude"]}</div>'
                maps_url = f"https://www.google.com/maps?q={web_info['latitude']},{web_info['longitude']}"
                analysis_html += f'<div class="analysis-item"><strong>Карты:</strong> <a href="{maps_url}" target="_blank">{maps_url}</a></div>'
            
            if web_info.get('capital') != "Неизвестно":
                analysis_html += f'<div class="analysis-item"><strong>Столица:</strong> {web_info["capital"]}</div>'
        
        analysis_html += "</div>"

    links_html = ''.join([
        f'<li class="link-item"><a href="{link}" target="_blank">{link}</a>'
        f'<div class="domain">Домен: {urlparse(link).netloc}</div></li>'
        for link in links
    ])
    
    html_template = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Результаты поиска телефона</title>
    {}
</head>
<body>
    <div class="container">
        <h1>🔍 Результаты поиска</h1>
        <div class="phone-info">
            <h3>Анализ номера: {}</h3>
        </div>
        {}
        <div class="stats">Найдено ссылок: {}</div>
        <ul class="link-list">
            {}
        </ul>
        <div class="timestamp">Отчет создан: {}</div>
    </div>
</body>
</html>"""
    
    html_content = html_template.format(
        css_styles, 
        phone_number,
        analysis_html,
        len(links), 
        links_html,
        time.strftime("%Y-%m-%d %H:%M:%S")
    )
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return filename

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = r"""
    _    ____ _____ ____      _    
   / \  / ___|_   _|  _ \    / \   
  / _ \ \___ \ | | | |_) |  / _ \  
 / ___ \ ___) || | |  _ <  / ___ \ 
/_/   \_\____/ |_| |_| \_\/_/   \_\   
"""
    
    title = "Поиск информации по номеру телефона + Анализ"
    credits = "ТГК - @statikkills_dev | Декоднул - @statikkills"
    
    print(Colorate.Horizontal(Colors.purple_to_blue, banner, 1))
    print(Center.XCenter(Colorate.Horizontal(Colors.purple_to_blue, title, 1)))
    print(Center.XCenter(Colorate.Horizontal(Colors.purple_to_blue, credits, 1)))
    print()

def print_links_to_console(links):
    if not links:
        Write.Print("❌ Ссылки не найдены\n", Colors.red_to_purple, interval=0.01)
        return
        
    Write.Print(f"\n🌐 Найдено {len(links)} уникальных ссылок:\n", Colors.purple_to_blue, interval=0.01)
    
    for i, link in enumerate(links, 1):
        domain = urlparse(link).netloc
        link_text = f"{i:2d}. {link}"
        domain_text = f"    Домен: {domain}"
        
        print(Colorate.Horizontal(Colors.purple_to_blue, link_text, 1))
        print(Colorate.Horizontal(Colors.blue_to_purple, domain_text, 1))
        print(Colorate.Horizontal(Colors.purple_to_blue, "    " + "─" * 40, 1))

def open_html_report():
    filename = "search_results.html"
    if os.path.exists(filename):
        webbrowser.open(f'file://{os.path.abspath(filename)}')
        Write.Print("✅ Отчет открыт в браузере\n", Colors.green_to_blue, interval=0.01)
    else:
        Write.Print("❌ Файл отчета не найден\n", Colors.red_to_purple, interval=0.01)

def main():
    install_libraries()
    
    while True:
        clear_console()
        print_banner()
        
        phone_number = Write.Input("📞 Введите номер телефона: ", Colors.purple_to_blue, interval=0.005, hide_cursor=False)
        
        if not phone_number:
            Write.Print("❌ Пожалуйста, введите номер телефона\n", Colors.red_to_purple, interval=0.01)
            time.sleep(1)
            continue
        
        Write.Print("\n🔍 Выполняем анализ номера...\n", Colors.blue_to_purple, interval=0.01)
        
        analyzer = PhoneAnalyzer(phone_number)
        if analyzer.run_analysis():
            display_phone_results(analyzer.results)
            analysis_results = analyzer.results
        else:
            Write.Print("❌ Неверный номер телефона\n", Colors.red_to_purple, interval=0.01)
            analysis_results = {"basic_info": {}, "web_info": {}}
            
        Write.Print("🔎 Выполняем поиск ссылок в Google...\n", Colors.blue_to_purple, interval=0.01)
        search_results = search_phone_number(phone_number)
        
        if isinstance(search_results, list):
            print_links_to_console(search_results)
            filename = save_links_to_html(search_results, phone_number, analysis_results)
            Write.Print(f"✅ Результаты сохранены в {filename}\n", Colors.green_to_blue, interval=0.01)
            
            open_report = Write.Input("Открыть отчет в браузере? (y/n): ", Colors.purple_to_blue, interval=0.005, hide_cursor=False).lower()
            if open_report == 'y':
                open_html_report()
        else:
            Write.Print(f"❌ {search_results}\n", Colors.red_to_purple, interval=0.01)
        
        Write.Input("\nНажмите Enter для продолжения...", Colors.purple_to_blue, interval=0.005, hide_cursor=False)

if __name__ == "__main__":
    main()