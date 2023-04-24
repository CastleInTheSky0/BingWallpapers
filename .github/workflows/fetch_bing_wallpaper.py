import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
BASE_URL = "https://www.bing.com"

def fetch_bing_wallpaper():
    response = requests.get(URL)
    data = response.json()
    image_url = BASE_URL + data["images"][0]["url"]
    image_date = data["images"][0]["enddate"]
    image_caption = data["images"][0]["copyright"]
    return image_url, image_date, image_caption

def update_readme(image_url, image_date, image_caption):
    with open("README.md", "r") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    table = soup.table

    if not table:
        table = soup.new_tag("table")

    # Check if the new image is already present in the table
    for img in table.find_all("img"):
        if img["src"] == image_url:
            return

    header = table.th
    if not header:
        header = soup.new_tag("th", colspan="3")
        first_row = soup.new_tag("tr")
        first_row.append(header)
        table.insert(0, first_row)

    new_image = soup.new_tag("img", src=image_url, width="100%")
    header.clear()
    header.append(new_image)

    cells = table.find_all("td")
    if cells:
        prev_image = cells[-1].img.extract()
        for i in range(len(cells) - 1, 0, -1):
            curr_image = cells[i - 1].img.extract()
            cells[i].append(curr_image)
        cells[0].insert(0, prev_image)
    else:
        new_row = soup.new_tag("tr")
        for _ in range(3):
            new_cell = soup.new_tag("td")
            new_row.append(new_cell)
        table.append(new_row)

    if len(cells) >= 30:
        last_image = cells[-1].img.extract()
        last_image_date = last_image["src"].split("/")[-1].split("_")[0]
        if not os.path.exists(f"old_wallpapers/{last_image_date}"):
            os.makedirs(f"old_wallpapers/{last_image_date}")
        os.rename(last_image["src"], f"old_wallpapers/{last_image_date}/{last_image_date}.jpg")

    with open("README.md", "w") as f:
        f.write(str(soup))

if __name__ == "__main__":
    image_url, image_date, image_caption = fetch_bing_wallpaper()
    update_readme(image_url, image_date, image_caption)
