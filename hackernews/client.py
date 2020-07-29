import aiohttp
import datetime
from bs4 import BeautifulSoup

from . import config
from . import db


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


def parse_news_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    table_itemlist = soup.find('table', class_='itemlist')
    news_trs = table_itemlist.find_all('tr', id=True)
    news = []
    for tr in news_trs:
        article_id = tr['id']
        article_title = tr.find(class_='storylink').string
        article_url = tr.find(class_='storylink').get('href')
        article_created = datetime.datetime.utcnow().isoformat()
        article = db.Article(article_id, article_title, article_url, article_created)
        news.append(article)
    return news


async def get_news():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, config.FETCH_URL)
        news = parse_news_page(html)
        return news


