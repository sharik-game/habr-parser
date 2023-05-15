from collections import deque
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from setup import bot_token, chat_id, frequency_of_requests, price_from, price_before
import time
old_id = deque([str(i) for i in range(1, 26)], maxlen=27)
def get_date(url1: str):
    response = requests.get(f"{url1}/tasks/")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features="lxml")
        articles = soup.find_all('article', class_='task task_list')
        for article in articles:
            flag = False
            url = url1 + article.a['href']
            task_id = article.a['href'].replace("/tasks/", "")
            title = article.find('div', class_='task__title').text.strip()
            price = article.find('div', class_='task__price').text.strip()
            price = price.replace(" ", "")
            price = price.replace("руб.запроект", "")
            try:
                price = int(float(price))
                if price >= price_from and price <= price_before:
                    flag = True
            except ValueError:
                pass
            responses = article.find('span', class_='params__responses')
            responses = responses.text.strip() if responses else '0 отликов'
            # views = article.find('span', class_='params__views').text.strip()
            # published_at = article.find('span', class_='params__published-at').text.strip()
            tags = [tag.text for tag in article.find_all('a', class_='tags__item_link')]
            ans = {'url': url, 'task id': task_id, 'title': title, 'price': price, 'responses': responses, 'tags': tags}
            if flag and task_id not in old_id:
                test = old_id.popleft()
                old_id.append(task_id)
                print(old_id)
                yield ans
    else:
        print(f"Uncorrect response status code. Need 200 get {response.status_code}")
def send_date_in_tg(sleep_time: float, url: str):
    orders = get_date(url)
    for order in orders:
        message = f"Url: {order['url']}\nHeader: {order['title']}\nPrice: {order['price']}\nTags: {order['tags']}"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
        response = requests.get(url)
        if str(response) != '<Response [200]>':
            print("Parse error")
            pprint(response)
        time.sleep(sleep_time)
def main():
        try:
            is_conection_error: bool = False
            while True:
                try:
                    send_date_in_tg(0.5, "https://freelance.habr.com")
                    if is_conection_error:
                        is_conection_error = False
                        print("Connection restored")
                    time.sleep(frequency_of_requests)
                except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
                    if not is_conection_error:
                        print("Connection error")
                        is_conection_error = True
        except KeyboardInterrupt:
            print("Buy")
            exit(0)

    

if __name__ == '__main__':
    main()

