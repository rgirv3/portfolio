import datetime
import requests
import bs4
from bs4 import BeautifulSoup

current = datetime.datetime.now()
previous = datetime.timedelta(minutes=60)
lastHour = current - previous


def omitNested(element):
    for item in element.children:
        if isinstance(item, bs4.element.NavigableString):
            yield item


def send_push(title, message_to_send):
    requests.post("https://api.pushover.net/1/messages.json", data={
                     "token": "",
                     "user": "",
                     "title": title,
                     "message": message_to_send,
                 })


def parseResponse(url):
    response = requests.get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    posts = html_soup.find_all('li', class_='result-row')
    for post in posts:
        posted = post.find('time', class_='result-date')
        dt = posted['datetime']
        post_time = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M')
        if post_time > lastHour:
            post_title = post.find('a', class_='result-title hdrlnk')
            price = post.find('span', class_='result-price').text
            link = post_title['href']
            post_title = post_title.text + ' - ' + price
            post_data_get = requests.get(link)
            post_soup = BeautifulSoup(post_data_get.text, 'html.parser')
            body = post_soup.find(id='postingbody')
            body_data = ''.join(omitNested(body)).strip() + '\n' + link
            send_push(post_title, body_data)


parseResponse('https://newjersey.craigslist.org/search/sss?query=king+bed+frame&min_price=&max_price=')
