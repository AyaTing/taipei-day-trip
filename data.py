import json
import re 
from database import save_attraction_data, clear_attraction_data

json_file = "data/taipei-attractions.json"

def filter_image_urls(image_urls):
    urls = re.split(r"http",image_urls,flags=re.I)
    available_urls = []
    for url in urls:
        if url.endswith((".JPG",".jpg",".PNG",".png")):
            complete_url = "http" + url
            available_urls.append(complete_url)
    return available_urls

def load_attraction_data():
    try:
        with open(json_file,"r",encoding="utf-8") as file:
            data = json.load(file)
            attractions = data["result"]["results"]
            for attraction in attractions:
                attraction_data = {
                "name": attraction["name"],
                "category": attraction["CAT"],
                "description": attraction["description"],
                "address": attraction["address"],
                "transport": attraction["direction"],
                "mrt": attraction["MRT"],
                "lat": attraction["latitude"],
                "lng": attraction["longitude"]
                }
                image_urls = filter_image_urls(attraction["file"])
                attraction_id = save_attraction_data(attraction_data, image_urls)
                print(f" {attraction_id}：{attraction['name']} saved")
    except Exception as err:
        print(f"檔案讀取失敗：{err}")

if __name__ == "__main__":
    clear_attraction_data()
    load_attraction_data()