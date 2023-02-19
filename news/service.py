import httpx
import asyncio
from news.models import Article

class NewsParser():

    @classmethod
    async def get_articles_links(cls):
        raise NotImplementedError("Please Implement this method")
        

class RBCNewsParser(NewsParser):

    URL = 'https://www.rbc.ru/crypto/tags/?tag=Криптовалюта'

    @classmethod
    async def get_articles_links(cls):
        try:
            async with httpx.AsyncClient() as client:
                    response = await client.get(cls.URL)
            if (response.status_code != 200):
                    raise ConnectionError
            return response.text
        except:
            raise ConnectionError



""" p = RBCNewsParser()
html_content =  asyncio.run(p.get_articles_links())
print(html_content)
tree = html.fromstring(html_content)
print(tree.xpath('//a[@class="item__link"]/@href')) """