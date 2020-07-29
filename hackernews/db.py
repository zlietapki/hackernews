import sqlite3
from collections import namedtuple
from . import config

SQLITE_FILE = config.SQLITE_FILE
Article = namedtuple('Article', ['id', 'title', 'url', 'created'])


async def get_conn():
    conn = sqlite3.connect(SQLITE_FILE)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS news (
        id INTEGER UNIQUE,
        title TEXT,
        url TEXT,
        created TEXT
    )''')
    return conn


async def update_news(news):
    conn = await get_conn()
    cur = conn.cursor()
    try:
        for article in news:
            cur.execute("INSERT INTO news (id, title, url, created) VALUES(?,?,?,?)", article)
            conn.commit()
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' not in str(e):
            raise
    finally:
        conn.close()


def make_sql(query):
    sql = 'SELECT id, title, url, created FROM news'

    order, _, order_direction = query.get('order', '').partition(' ')
    if order:
        if order not in Article._fields:
            raise RuntimeError('incorrect order')
        sql += f' ORDER BY {order}'

        if order_direction:
            order_direction = order_direction.upper()
            if order_direction not in ('ASC', 'DESC'):
                raise RuntimeError('incorrect order direction')
            sql += f' {order_direction}'

    limit = query.get('limit', '5')
    if limit and not limit.isdigit():
        raise RuntimeError('incorrect limit')
    sql += f' LIMIT {limit}'

    offset = query.get('offset')
    if offset:
        if offset and not offset.isdigit():
            raise RuntimeError('incorrect offset')
        sql += f' OFFSET {offset}'
    return sql


async def get_news(query):
    conn = await get_conn()
    cur = conn.cursor()
    sql = make_sql(query)
    cur.execute(sql)
    news = [Article._make(row) for row in cur.fetchall()]
    return news
