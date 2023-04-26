import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=en-US"
BASE_URL = "https://www.bing.com"

def fetch_bing_wallpapers():
    response = requests.get(URL)
    data = response.json()

    wallpapers = []
    for image in data["images"]:
        image_url = BASE_URL + image["url"]
        image_date = image["enddate"]
        image_startdate = image["startdate"]
        image_caption = image["copyright"]
        image_title = image["title"]
        wallpapers.append((image_url, image_date, image_startdate, image_caption, image_title))

    return wallpapers

def save_image(image_url, image_date, image_title):
    year_month = image_date[:6]
    if not os.path.exists(f"old_wallpapers/{year_month}"):
        os.makedirs(f"old_wallpapers/{year_month}")

    image_name = image_title.replace(" ", "_")
    image_path = f"old_wallpapers/{year_month}/{image_name}.jpg"

    if os.path.exists(image_path):
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

    new_wallpapers = sorted([wp for wp in wallpapers if wp[0] not in existing_images], key=lambda x: x[1], reverse=True)

    if not new_wallpapers:
        return

    latest_image_url, latest_image_date, _, latest_image_caption, latest_image_title = new_wallpapers[0]

    header = table.th

    if header:
        # 去除可能存在的换行和空格
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
    new_image = soup.new_tag("img", src=latest_image_url, width="100%")
    header.append(new_image)
    header_caption = soup.new_tag("p")
    header_caption.string = f"{latest_image_date} - {latest_image_caption}"
    header.append(header_caption)

    num_rows = (len(new_wallpapers) - 1) // 3
    if (len(new_wallpapers) - 1) % 3 != 0:
        num_rows += 1

    for _ in range(num_rows):
        new_row = soup.new_tag("tr")
        for _ in range(3):
            new_cell = soup.new_tag("td")
            new_row.append(new_cell)
        table.append(new_row)

    cells = table.find_all("td")

    for i, (image_url, image_date, _, image_caption, image_title) in enumerate(new_wallpapers[1:]):
        if i >= len(cells):
            break

        cell = cells[i]
        cell.clear()
        save_image(image_url, image_date, image_title)
        new_image = soup.new_tag("img", src=image_url, width="100%")
        cell.append(new_image)
        cell_caption = soup.new_tag("p")
        cell_caption.string = f"{image_date} - {image_caption}"
        cell.append(cell_caption)
    print(soup)
    with open("README.md", "w") as f:
        f.write(str(soup))

if __name__ == "__main__":
    wallpapers = fetch_bing_wallpapers()
    update_readme(wallpapers)