import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=en-US"
BASE_URL = "https://www.bing.com"

def fetch_bing_wallpapers():
    # 使用127.0.0.1:10809代理请求数据
    proxies = {
        "http": "http://127.0.0.1:10809",
        "https": "http://127.0.0.1:10809"
    }

    response = requests.get(URL, proxies=proxies)
    data = response.json()
    wallpapers = []
    for image in data["images"]:
        image_url = BASE_URL + image["url"]
        image_date = image["enddate"]
        image_caption = image["copyright"]
        image_title = image["title"]
        wallpapers.append((image_url, image_date, image_caption, image_title))

    return wallpapers

def save_image(image_url, image_date, image_title):
    year_month = image_date[:6]
    if not os.path.exists(f"old_wallpapers/{year_month}"):
        os.makedirs(f"old_wallpapers/{year_month}")

    image_name = image_title.replace(" ", "_")
    image_path = f"old_wallpapers/{year_month}/{image_name}.jpg"

    if os.path.exists(image_path):
        print("壁纸已存在！")
        return

    response = requests.get(image_url)
    image_data = response.content

    with open(image_path, "wb") as f:
        f.write(image_data)

def update_readme(wallpapers):
    with open("README.md", "r") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    table = soup.table

    if not table:
        table = soup.new_tag("table")
        soup.append(table)

    existing_images = [img["src"] for img in table.find_all("img")]
    # 获取table中所有的img标签本身和p标签本身
    old_wallpapers = []
    if table.th:
        image_url = table.th.img["src"]
        image_title = table.th.img["alt"]
        p_content = table.th.p.string.split(" - ")
        image_date = p_content[0].strip()
        image_caption = p_content[1].strip()
        old_wallpapers.append((image_url, image_date, image_caption, image_title))
    for row in table.find_all("tr")[1:]:
        for cell in row.find_all("td"):
            if cell.img:
                image_url = cell.img["src"]
                image_title = cell.img["alt"]
                p_content = cell.p.string.split(" - ")
                image_date = p_content[0].strip()
                image_caption = p_content[1].strip()
                old_wallpapers.append((image_url, image_date, image_caption, image_title))

    new_wallpapers = sorted([wp for wp in wallpapers if wp[0] not in existing_images], key=lambda x: x[1], reverse=True)

    if not new_wallpapers:
        print('没有新的壁纸！')
        return

    latest_image_url, latest_image_date, latest_image_caption, latest_image_title = new_wallpapers[0]

    header = table.th

    if header:
        current_header_date = datetime.strptime(header.p.string.split(" - ")[0].strip(), "%Y%m%d")
        latest_image_datetime = datetime.strptime(latest_image_date, "%Y%m%d")

        if latest_image_datetime <= current_header_date:
            return

        header.img.decompose()
        header.p.decompose()
    else:
        header = soup.new_tag("th", colspan="3")
        first_row = soup.new_tag("tr")
        first_row.append(header)
        table.insert(0, first_row)

    save_image(latest_image_url, latest_image_date, latest_image_title)
    new_image = soup.new_tag("img", src=latest_image_url, alt=latest_image_title, width="100%")
    header.append(new_image)
    header_caption = soup.new_tag("p")
    header_caption.string = f"{latest_image_date} - {latest_image_caption}"
    header.append(header_caption)

    seen = set()
    all_wallpapers = []

    for wp in old_wallpapers + new_wallpapers:
        if wp[0] not in seen:
            all_wallpapers.append(wp)
            seen.add(wp[0])

    all_wallpapers.sort(key=lambda x: x[1], reverse=True)
    
    for i, row in enumerate(table.find_all("tr")[1:]):
        if i * 3 + 1 > 30:
            row.decompose()
            continue
        for j, cell in enumerate(row.find_all("td")):
            index = i * 3 + j + 1
            if index < len(all_wallpapers):
                image_url, image_date, image_caption, image_title = all_wallpapers[index]
                cell.clear()
                save_image(image_url, image_date, image_title)
                new_image = soup.new_tag("img", src=image_url, alt=image_title, height="180px")
                cell["style"] = "vertical-align: top;"
                cell.append(new_image)
                cell_caption = soup.new_tag("p")
                cell_caption.string = f"{image_date} - {image_caption}"
                cell.append(cell_caption)
            else:
                cell.clear()

    with open("README.md", "w") as f:
        f.write(str(soup))

if __name__ == "__main__":
    wallpapers = fetch_bing_wallpapers()
    update_readme(wallpapers)