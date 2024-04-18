import asyncio

import aiohttp
from bs4 import BeautifulSoup as bs
from typing import Tuple

DEFAULT_URL = 'https://steamcommunity.com/market/search?appid=730'

async def pagination_limit()->Tuple[int, int]:
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(DEFAULT_URL+'#p1_popular_desc') as response:
            soup = bs(await response.text(), "lxml")
            nb_listings = int(soup.find("span", {"id": "searchResults_total"}).text)

    return nb_listings // 10, nb_listings % 10


async def get_prices(pg: int)->None:
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(f'https://steamcommunity.com/market/search?appid=730#p{pg}_popular_desc') as response:
            soup = bs(await response.text(), "lxml")
            soup.find_all("span", {"class": "normal_price"})






asyncio.run(get_prices())

