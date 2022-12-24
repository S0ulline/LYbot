import requests
img_data = requests.get("https://sun9-35.userapi.com/impg/n6YFbfgbSVogKpQMX2xkn07q1SWc34LOXkVV7g/-Y80Gq9IFIQ.jpg?size=998x602&quality=96&sign=6fb5cf62afc8e58393e9fbf06e9f8697&type=album").content
with open('gift_info.jpg', 'wb') as handler:
    handler.write(img_data)
