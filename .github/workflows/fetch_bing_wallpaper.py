import os
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlsplit,urlunsplit


URL = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
BASE_URL = "https://www.bing.com"

def fetch_bing_wallpaper():
    response = requests.get(URL)
    data = response.json()
    image_url = BASE_URL + data["images"][0]["url"]
    image_date = data["images"][0]["enddate"]
    image_caption = data["images"][0]["copyright"]

    # Remove query parameters from the image URL
    url_parts = list(urlsplit(image_url))
    url_parts[3] = ""  # Clear query parameters
    clean_image_url = urlunsplit(url_parts)

    return clean_image_url, image_date, image_caption

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

    # Save the image with a new name format and original extension
    image_response = requests.get(image_url)
    image_extension = os.path.splitext(image_url)[-1]
    safe_image_caption = re.sub(r"[^\w\s]", "_", image_caption)  # Replace special characters with underscores
    new_image_name = f"{image_date} {safe_image_caption}{image_extension}"
    with open(new_image_name, "wb") as f:
        f.write(image_response.content)

    new_image = soup.new_tag("img", src=new_image_name, width="300")
    new_caption = soup.new_tag("p")
    new_caption.string = f"{image_date} {image_caption}"

    new_cell.append(new_image)
    new_cell.append(new_caption)
    new_row.append(new_cell)

    if len(table.find_all("td")) >= 30:
        last_image = table.find_all("td")[-1].img["src"]
        last_image_date = last_image.split("/")[-1].split("_")[0]
        last_image_extension = os.path.splitext(last_image)[-1]
        if not os.path.exists(f"old_wallpapers/{last_image_date}"):
            os.makedirs(f"old_wallpapers/{last_image_date}")
        os.rename(last_image, f"old_wallpapers/{last_image_date}/{last_image_date}{last_image_extension}")

    table.insert(0, new_row)

    with open("README.md", "w") as f:
        f.write(str(soup))

if __name__ == "__main__":
    image_url, image_date, image_caption = fetch_bing_wallpaper()
    update_readme(image_url, image_date, image_caption)
