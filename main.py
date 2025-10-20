from bs4 import BeautifulSoup
import json
import time
import asyncio
import httpx

# import pandas as pd
URL = "https://texnomart.uz/ru/katalog/"
HOST = "https://texnomart.uz"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}

client = httpx.AsyncClient(timeout=httpx.Timeout(30))

async def get_soup(link):
        response = await client.get(link, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup


async def get_pagination(category,link):
    soup = await get_soup(link)
    pagination = soup.find("div", class_="pagination")
    if pagination is None:
        return {
            "category": category,
            "link": link,
            "pages" : 1,
        }
    buttons = pagination.select('button[title=""]')
    if not buttons:
        return {
            "category": category,
            "link": link,
            "pages" : 1,
        }
    return {
        "category": category,
        "link": link,
        "pages": int(buttons[-1].find('span').text),
    }


async def get_category():
    soup = await get_soup(URL)
    categories = soup.find_all("a", class_="content__link")
    data = [
        {
            "title": category.get_text().strip(),
            "link": HOST + category.get("href")
        }
        for category in categories
    ]
    return data


def get_pretty_price(price):
    price, _ = price.split('\n')

    return int(price.replace(" ", ""))


# def get_description(product_id):
#     url = f"https://gw.texnomart.uz/api/web/v1/product/characters?id={product_id}"
#     time.sleep(2)
#     response = requests.get(url)
#     data = response.json()
#
#     description = {}
#     if "data" in data and "data" in data["data"]:
#         for block in data["data"]["data"]:
#             for char in block["characters"]:
#                 description[char["name"]] = char["value"]
#
#     return description
#
#


async def get_products(category, link):
    soup = await get_soup(link)
    products = soup.find_all("div", class_="col-3")
    data = [
        {
            "Name": product.find("h2").text.strip(),
            "Price": get_pretty_price(product.find("div", class_="product-price__current").text.strip()),
            "Category_name": category,
            "Category_link": link,
            # "Description": description,
            "Link": HOST + product.find("a").get("href"),
            "Img": product.find("a").find("img").get("data-src")
        }
        for product in products
    ]
    return data


#
#
#
# def save_json(data, filename):
#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)
#
#
# def save_xlsx(data, filename):
#     df = pd .DataFrame(data)
#     df.to_excel(filename)
#
#
#
# def main():
#     start = time.time()
#     categorys = get_category()
#     data = [
#         product
#         for category in categorys[:5]
#         for product in get_products(category["title"], category["link"])
#     ]
#     save_json(data, "data2.json")
#     end = time.time()
#     print(f"всё: {end - start:.2f} секунд")
#
#
#
#
async def main():
    categories = await get_category()
    pagination_tasks = [
        get_pagination(category.get("title"),category.get("link"))
        for category in categories
    ]
    data = []
    for i in range(0, len(pagination_tasks), 50):
        data += await asyncio.gather(*pagination_tasks[i:i+50])

    product_tasks = []
    for category in data:
        for page in range(1,int(category["pages"])+ 1):
            product_tasks.append(
                get_products(category, category["link"])
            )
    products = []
    for i in range(0, len(product_tasks), 30):
        products += await asyncio.gather(*product_tasks[i:i+30])
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
if __name__ == '__main__':
    asyncio.run(main())
