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
        image_caption = image["copyright"]
        image_title = image["title"]
        wallpapers.append((image_url, image_date, image_caption, image_title))
    
    return wallpapers

def save_image(image_url, image_date, image_title):
    response = requests.get(image_url)
    image_data = response.content

    year_month = image_date[:6]
    if not os.path.exists(f"old_wallpapers/{year_month}"):
        os.makedirs(f"old_wallpapers/{year_month}")

    image_name = image_title.replace(" ", "_")
    with open(f"old_wallpapers/{year_month}/{image_name}.jpg", "wb") as f:
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

    new_wallpapers = [wp for wp in wallpapers if wp[0] not in existing_images]

    if not new_wallpapers:
        return

    for image_url, image_date, image_caption, image_title in new_wallpapers:
        save_image(image_url, image_date, image_title)
        header = table.th
        if header:
            prev_image = header.img.extract()
            prev_caption = header.p.extract()
            header.clear()
        else:
            header = soup.new_tag("th", colspan="3")
            first_row = soup.new_tag("tr")
            first_row.append(header)
            table.insert(0, first_row)

        new_image = soup.new_tag("img", src=image_url, width="100%")
        header.append(new_image)
        header_caption = soup.new_tag("p")
        header_caption.string = f"{image_date} - {image_caption}"
        header.append(header_caption)

        cells = table.find_all("td")
        num_cells = len(cells)

        if num_cells < 30:
            if num_cells == 0:
                new_row = soup.new_tag("tr")
                for _ in range(3):
                    new_cell = soup.new_tag("td")
                    new_row.append(new_cell)
                table.append(new_row)
                cells = table.find_all("td")

            for i in range(num_cells - 1, 0, -1):
                if cells[i - 1].img:
                    cells[i].clear()
                    cells[i].append(cells[i - 1].img.extract())
                    cells[i].append(cells[i - 1].p.extract())

            cells[0].clear()
            cells[0].append(prev_image)
            cells[0].append(prev_caption)
        else:
            for i in range(29, 0, -1):
                if cells[i - 1].img:
                    cells[i].clear()
                    cells[i].append(cells[i - 1].img.extract())
                    cells[i].append(cells[i - 1].p.extract())

            cells[0].clear()
            cells[0].append(prev_image)
            cells[0].append(prev_caption)

    with open("README.md", "w") as f:
        f.write(str(soup))

if __name__ == "__main__":
    wallpapers = fetch_bing_wallpapers()
    update_readme(wallpapers)