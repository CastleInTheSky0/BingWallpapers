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
    image_title = data["images"][0]["title"].replace(" ", "_")
    return image_url, image_date, image_caption, image_title

def update_readme(image_url, image_date, image_caption, image_title):
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
    header_caption = soup.new_tag("p")
    header_caption.string = f"{image_date} - {image_caption}"
    header.append(header_caption)

    cells = table.find_all("td")
    if cells:
        prev_image = cells[-1].img.extract()
        prev_caption = cells[-1].p.extract()
        for i in range(len(cells) - 1, 0, -1):
            curr_image = cells[i - 1].img.extract()
            curr_caption = cells[i - 1].p.extract()
            cells[i].append(curr_image)
            cells[i].append(curr_caption)
        cells[0].insert(0, prev_image)
        cells[0].insert(1, prev_caption)
    else:
        new_row = soup.new_tag("tr")
        for _ in range(3):
            new_cell = soup.new_tag("td")
            new_row.append(new_cell)
        table.append(new_row)

    image_file_path = os.path.join("old_wallpapers", image_date, f"{image_title}.jpg")
    os.makedirs(os.path.dirname(image_file_path), exist_ok=True)

    if not os.path.exists(image_file_path):
        with requests.get(image_url, stream=True) as r:
            r.raise_for_status()
            with open(image_file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    with open("README.md", "w") as f:
        f.write(str(soup))

if __name__ == "__main__":
    image_url, image_date, image_caption, image_title = fetch_bing_wallpaper()
    update_readme(image_url, image_date, image_caption, image_title)