import os.path
import sqlite3
import pytest
from hackernews import db


class TestGetConn:
    @pytest.mark.asyncio
    async def test_ok(self, tmpdir):
        db.SQLITE_FILE = os.path.join(tmpdir, 'tmp.sqlite')
        conn = await db.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news'")
        (tbl_name, ) = cur.fetchone()
        assert tbl_name == 'news'

    @pytest.mark.asyncio
    async def test_fail(self):
        db.SQLITE_FILE = '/not_exists'
        with pytest.raises(sqlite3.OperationalError):
            await db.get_conn()


class TestUpdateNews:
    @pytest.mark.asyncio
    async def test_ok(self, tmpdir):
        db.SQLITE_FILE = os.path.join(tmpdir, 'tmp.sqlite')
        news = [
            ('111', 'title1', 'url1', 'time1'),
            ('222', 'title2', 'url2', 'time2'),
        ]
        await db.update_news(news)
        conn = await db.get_conn()
        cur = conn.cursor()
        cur.execute('SELECT * FROM news')
        res = [art for art in cur]
        assert len(res) == 2
        article = db.Article(*res[0])
        assert article.title == 'title1'

    @pytest.mark.asyncio
    async def test_fail(self, tmpdir):
        db.SQLITE_FILE = os.path.join(tmpdir, 'tmp.sqlite')
        news = [()]
        with pytest.raises(sqlite3.ProgrammingError) as exinfo:
            await db.update_news(news)
        assert 'Incorrect number of bindings supplied' in str(exinfo.value)


class TestMakeSql:
    def test_ok_no_args(self):
        query = {}
        sql = db.make_sql(query)
        assert sql == 'SELECT id, title, url, created FROM news LIMIT 5'

    def test_ok_order(self):
        query = {'order': 'title'}
        sql = db.make_sql(query)
        assert sql == 'SELECT id, title, url, created FROM news ORDER BY title LIMIT 5'

    def test_ok_order_desc(self):
        query = {'order': 'id desc'}
        sql = db.make_sql(query)
        assert sql == 'SELECT id, title, url, created FROM news ORDER BY id DESC LIMIT 5'

    def test_ok_order_asc(self):
        query = {'order': 'url asc'}
        sql = db.make_sql(query)
        assert sql == 'SELECT id, title, url, created FROM news ORDER BY url ASC LIMIT 5'

    def test_ok_limit(self):
        query = {'limit': '10'}
        sql = db.make_sql(query)
        assert sql == 'SELECT id, title, url, created FROM news LIMIT 10'

    def test_ok_offset(self):
        query = {
            'limit': '10',
            'offset': '10',
        }
        sql = db.make_sql(query)
        assert sql == 'SELECT id, title, url, created FROM news LIMIT 10 OFFSET 10'

    def test_ok_order_limit(self):
        query = {
            'order': 'title DESC',
            'limit': '10',
        }
        sql = db.make_sql(query)
        assert sql == 'SELECT id, title, url, created FROM news ORDER BY title DESC LIMIT 10'

    def test_fail_order(self):
        query = {'order': 'hah'}
        with pytest.raises(RuntimeError) as exinfo:
            db.make_sql(query)
        assert 'incorrect order' in str(exinfo.value)

    def test_fail_order_direction(self):
        query = {'order': 'title some'}
        with pytest.raises(RuntimeError) as exinfo:
            db.make_sql(query)
        assert 'incorrect order direction' in str(exinfo.value)

    def test_fail_limit(self):
        query = {'limit': '-10'}
        with pytest.raises(RuntimeError) as exinfo:
            db.make_sql(query)
        assert 'incorrect limit' in str(exinfo.value)


class TestGetNews:
    @pytest.mark.asyncio
    async def test_ok(self, tmpdir):
        db.SQLITE_FILE = os.path.join(tmpdir, 'tmp.sqlite')
        news = [
            ('111', 'title1', 'url1', 'time1'),
            ('222', 'title2', 'url2', 'time2'),
        ]
        await db.update_news(news)

        query = {}
        news = await db.get_news(query)
        assert len(news) == 2
        assert news[0].id == 111
