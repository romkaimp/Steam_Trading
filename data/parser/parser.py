import asyncio
import data.orm.async_orm as orm
import aiohttp
from bs4 import BeautifulSoup as bs
from typing import Tuple
import threading

DEFAULT_URL = 'https://steamcommunity.com/market/search?appid=730'

async def pagination_limit()->Tuple[int, int]:
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(DEFAULT_URL+'#p1_popular_desc') as response:
            soup = bs(await response.text(), "lxml")
            nb_listings = soup.find("span", {"id": "searchResults_total"}).text.split(",")
            nb_listings = int("".join(nb_listings))

    return nb_listings // 10, nb_listings % 10


async def get_prices(pg: int)->None:
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(f'https://steamcommunity.com/market/search?appid=730#p{pg}_popular_desc') as response:
            soup = bs(await response.text(), "lxml")
            listings = soup.find_all("a", {"class": "market_listing_row_link"})


            for listing in listings:
                ref = listing.get("href")
                name = listing.find("div", {"class": "market_listing_row market_recent_listing_row market_listing_searchresult"}).get("data-hash-name")
                price = int(listing.find("span", {"class": "market_table_value normal_price"}).find("span", {"class": "normal_price"}).get("data-price"))
                imgs = listing.find("img")
                img_small = imgs.get("src")
                img_big = img_small + "dpx2x"
                print(ref)
                await orm.async_insert_listing(name, price, img_small, img_big, ref)



async def table_update()->None:
    pages = await pagination_limit()

    for i in range(1, pages[0]+1):
        await get_prices(i)








if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(table_update())

