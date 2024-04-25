import asyncio
from aiohttp.client_exceptions import ClientConnectionError
from asyncpg.exceptions import SerializationError
import data.orm.async_orm as orm
import aiohttp
from bs4 import BeautifulSoup as bs
from typing import Tuple, List, Coroutine, Any
from threading import Thread

DEFAULT_URL = 'https://steamcommunity.com/market/search?appid=730'


async def pagination_limit()->Tuple[int, int]:
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(DEFAULT_URL+'#p1_popular_desc') as response:
            soup = bs(await response.text(), "lxml")
            nb_listings = soup.find("span", {"id": "searchResults_total"}).text.split(",")
            nb_listings = int("".join(nb_listings))

    return nb_listings // 10, nb_listings % 10


async def get_prices(pg: int)->None:
    while True:
        try:
            async with aiohttp.ClientSession(trust_env=True) as session:
                async with session.get(f'https://steamcommunity.com/market/search?appid=730#p{pg}_popular_desc') as response:
                    tex = await response.text()
                    #print(tex)
                    soup = bs(tex, "lxml")
                    listings = soup.find_all("a", {"class": "market_listing_row_link"})
                    #print(pg)

                    task_list = []
                    #loop = asyncio.get_event_loop()

                    for listing in listings:
                        #print(listing)
                        ref = listing.get("href")
                        name = listing.find("div", {"class": "market_listing_row market_recent_listing_row market_listing_searchresult"}).get("data-hash-name")
                        price = int(listing.find("span", {"class": "market_table_value normal_price"}).find("span", {"class": "normal_price"}).get("data-price"))

                        imgs = listing.find("img")
                        img_small = imgs.get("src")
                        img_big = img_small + "dpx2x"
                        Thread(target=print, args=str(name)).start()
                        #await orm.async_insert_listing(name, price, img_small, img_big, ref)
                        task_list.append(orm.async_insert_listing(name=name, val=price, ref_small_image=img_small, ref_big_image=img_big, ref_gun=ref))
                    await asyncio.gather(*task_list)
                    break
        except ClientConnectionError as err:
            print(pg, "Error occured")
            await asyncio.sleep(1)
        except SerializationError as err:
            await asyncio.sleep(1)


            #loop.run_until_complete(task_list)


async def table_update(pages) -> None:#List[Coroutine | Any]:
    list_of_tasks = []
    [list_of_tasks.append(get_prices(i)) for i in range(1, 4)]
    #[list_of_tasks.append(get_prices(i)) for i in range(1, pages[0]+1)]
    #return list_of_tasks
    await asyncio.gather(*list_of_tasks)

    #for i in range(1, pages[0]+1):
        #await get_prices(i)
        #t = Thread(target=get_prices, args=(i, ))
        #t.start()








if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    pages = loop.run_until_complete(pagination_limit())
    #list_of_tasks = table_update(pages)
    #loop.run_until_complete(*list_of_tasks)
    loop.run_until_complete(table_update(pages))

