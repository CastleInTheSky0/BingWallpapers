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

    new_row = soup.new_tag("tr")
    new_cell = soup.new_tag("td")

    new_image = soup.new_tag("img", src=image_url, width="30%")
    new_caption = soup.new_tag("p")
    new_caption.string = f"{image_date} - {image_caption}"

    new_cell.append(new_image)
    new_cell.append(new_caption)
    new_row.append(new_cell)

    if len(table.find_all("td")) >= 30:
        last_image = table.find_all("td")[-1].img["src"]
        last_image_date = last_image.split("/")[-1].split("_")[0]
        if not os.path.exists(f"old_wallpapers/{last_image_date}"):
            os.makedirs(f"old_wallpapers/{last_image_date}")
        os.rename(last_image, f"old_wallpapers/{last_image_date}/{last_image_date}.jpg")

    table.insert(0, new_row)

    with open("README.md", "w") as f:
        f.write(str(soup))

if __name__ == "__main__":
    image_url, image_date, image_caption = fetch_bing_wallpaper()
    update_readme(image_url, image_date, image_caption)
