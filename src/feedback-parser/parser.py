import json
import time
import re
import gzip
from io import BytesIO
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    return webdriver.Chrome(options=chrome_options)  # Selenium сам скачает драйвер


catalog_driver = create_driver()
try:
    catalog_url = "https://www.wildberries.ru/recommendation/catalog?type=bestsallers"
    catalog_driver.get(catalog_url)
    time.sleep(5)

    last_height = catalog_driver.execute_script("return document.body.scrollHeight")
    while True:
        catalog_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = catalog_driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    product_elements = catalog_driver.find_elements(By.CSS_SELECTOR,
                                                    "a.product-card__link.j-card-link.j-open-full-product-card")
    product_links = [element.get_attribute("href") for element in product_elements if element.get_attribute("href")]
    print("Найдено ссылок на товары:", len(product_links))
finally:
    catalog_driver.quit()

for idx, link in enumerate(product_links, start=1):
    print(f"\nОбработка товара {idx}/{len(product_links)}: {link}")
    product_driver = create_driver()
    try:
        product_driver.get(link)
        time.sleep(8)

        product_driver.execute_script("window.scrollBy(0, 50);")
        time.sleep(3)
        product_driver.execute_script("window.scrollBy(0, -50);")
        time.sleep(3)
        product_driver.execute_script("window.scrollTo(0, 2000);")
        time.sleep(3)
        product_driver.execute_script("window.scrollBy(0, -1500);")
        time.sleep(5)

        pattern = re.compile(r"https://feedbacks\d+\.wb\.ru/feedbacks/v\d+/\d+")
        feedbacks_request = next((req for req in product_driver.requests if req.response and pattern.match(req.url)),
                                 None)

        if feedbacks_request:
            print(f"Найден запрос с отзывами: {feedbacks_request.url}")
            content_encoding = feedbacks_request.response.headers.get("Content-Encoding", "")
            raw_body = feedbacks_request.response.body

            if "gzip" in content_encoding:
                with gzip.GzipFile(fileobj=BytesIO(raw_body), mode='rb') as f:
                    body = f.read().decode('utf-8', errors='replace')
            else:
                body = raw_body.decode('utf-8', errors='replace')

            try:
                data = json.loads(body)
                print("JSON с отзывами успешно получен!")

                new_feedbacks = [{
                    "text": fb.get("text", ""),
                    "pros": fb.get("pros", ""),
                    "cons": fb.get("cons", ""),
                    "productValuation": fb.get("productValuation"),
                    "createdDate": fb.get("createdDate", "")
                } for fb in data.get("feedbacks", [])]

                filename = f"{idx}.json"
                with open(filename, "w", encoding="utf-8") as outfile:
                    json.dump(new_feedbacks, outfile, ensure_ascii=False, indent=4)
                print(f"Файл {filename} успешно создан!")
            except Exception as e:
                print("Ошибка при парсинге JSON:", e)
                print("Тело ответа:", body)
        else:
            print("Подходящий запрос с отзывами не найден.")
    finally:
        product_driver.quit()
