import asyncio
from aiohttp import web

from . import db
from . import client
from . import config

routes = web.RouteTableDef()


async def get_new_posts():
    news = await client.get_news()
    await db.update_news(news)


async def periodic_update_news():
    while True:
        await get_new_posts()
        await asyncio.sleep(config.FETCH_PERIOD)


@routes.get('/')
async def index_handle(req):
    html = '''
    <a href="/posts">/posts</a><br>
    <a href="/posts?order=title">/posts?order=title</a><br>
    <a href="/posts?order=created desc">/posts?order=created desc</a><br>
    <a href="/posts?order=title desc&limit=10">/posts?order=title desc&limit=10</a><br>
    <a href="/posts?order=id desc&limit=10&offset=1">/posts?order=id desc&limit=10&offset=1</a><br>
    <a href="/fetch_posts">/fetch_posts</a><br>
    '''
    return web.Response(text=html, content_type='text/html')


@routes.get('/posts')
async def posts_handle(req):
    try:
        news = await db.get_news(req.query)
    except RuntimeError as e:
        return web.Response(text=str(e))

    news = [article._asdict() for article in news]
    return web.json_response(news)


@routes.get('/fetch_posts')
async def fetch_posts_handle(req):
    await get_new_posts()
    return web.Response(text='Fetch complete')


def main():
    app = web.Application()
    app.add_routes(routes)

    loop = asyncio.get_event_loop()
    loop.create_task(periodic_update_news())

    web.run_app(app)
