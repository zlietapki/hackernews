import pytest
import aiohttp

from hackernews import client


class TestFetch:
    @pytest.mark.asyncio
    async def test_ok(self):
        async with aiohttp.ClientSession() as session:
            assert 'Яндекс' in await client.fetch(session, 'http://ya.ru')

    @pytest.mark.asyncio
    async def test_bad_host(self):
        async with aiohttp.ClientSession() as session:
            with pytest.raises(aiohttp.client_exceptions.ClientConnectorError):
                await client.fetch(session, 'http://hah')


class TestParse:
    def test_ok(self):
        html = '''
            <table class="itemlist">
                <tr id="111">
                    <td>
                        <a href="url1" class="storylink">title1</a>
                    </td>
                </tr>
                <tr id="222">
                    <td>
                        <a href="url2" class="storylink">title2</a>
                    </td>
                </tr>
            </table>
        '''
        news = client.parse_news_page(html)
        assert isinstance(news, list)
        assert len(news) == 2
        assert isinstance(news[0], tuple)

    def test_fail(self):
        html = ''
        with pytest.raises(AttributeError):
            client.parse_news_page(html)
