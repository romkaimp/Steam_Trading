import asyncio
import json
import re
import os
from dotenv import load_dotenv
import random
from pathlib import Path

from aiohttp.client_exceptions import ClientConnectionError
from asyncpg.exceptions import SerializationError
import data.orm.async_orm as orm
import aiohttp
from bs4 import BeautifulSoup as bs


from typing import Tuple, List, Coroutine, Any
import time

dotenv_path = Path("./proxy_auth.env")


def proxies_tuple() -> tuple[str, ...]:
    with open("./proxies.txt", "r") as file:
        proxies = file.readlines()
    proxies = [line.replace("\n", "") for line in proxies]
    return tuple(proxies)


load_dotenv(dotenv_path=dotenv_path)

PROXIES = proxies_tuple()
PROX_USER = os.getenv("PROXY_USER")
PROX_PASS = os.getenv("PROXY_PASS")
DEFAULT_URL = 'https://steamcommunity.com/market/search?appid=730'
ITEMS_COUNT = 50


async def pagination_limit() -> Tuple[int, int]:
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(DEFAULT_URL+'#p1_popular_desc') as response:
            soup = bs(await response.text(), "lxml")
            nb_listings = soup.find("span", {"id": "searchResults_total"}).text.split(",")
            nb_listings = int("".join(nb_listings))

    return nb_listings // ITEMS_COUNT, nb_listings % ITEMS_COUNT


async def get_prices(pg: int, lim: int = ITEMS_COUNT) -> None:
    proxy = random.choice(PROXIES)
    while True:
        try:

            async with aiohttp.ClientSession() as session:#trust_env=True) as session:
                proxy_auth = aiohttp.BasicAuth(PROX_USER, PROX_PASS)
                async with session.get(f'https://steamcommunity.com/market/search/render/',
                                       proxy=proxy,
                                       proxy_auth=proxy_auth,
                                       params={"start": f"{pg*ITEMS_COUNT-ITEMS_COUNT}",
                                               "count": lim,
                                               "sort_dir": "desc",
                                               "sort_column": "popular",
                                               "appid": 730,
                                               "search_descriptions": 0,
                                               "norender": 1,
                                               "query": ""}) as response:
                    tex = await response.text()
                    tex = json.loads(tex)

                    #ans = re.search(r"Showing <span id=\"searchResults_start\">(\d+)*", tex)
                    #print(ans[1])
                    print(response.status)


                    task_list = []
                    for listing in tex["results"]:
                        name = listing["name"]
                        price = listing["sell_price"]
                        name20 = name.replace(" ", "%20")
                        ref = f"https://steamcommunity.com/market/listings/730/{name20}"

                        img_small = "https://community.cloudflare.steamstatic.com/economy/image/" + listing["asset_description"]["icon_url"] + "62fx62f"
                        img_big = img_small + "dpx2x"
                        await orm.async_insert_listing(name=name, val=price, ref_small_image=img_small, ref_big_image=img_big, ref_gun=ref)
                        #task_list.append(orm.async_insert_listing(name=name, val=price, ref_small_image=img_small, ref_big_image=img_big, ref_gun=ref))

                    #soup = bs(tex, "lxml")
                    #listings = soup.find_all("a", {"class": "market_listing_row_link"})
                    #loop = asyncio.get_event_loop()

                    #for listing in listings:
                    #    #print(listing)
                    #    ref = listing.get("href")
                    #    name = listing.find("div", {"class": "market_listing_row market_recent_listing_row market_listing_searchresult"}).get("data-hash-name")
                    #    price = int(listing.find("span", {"class": "market_table_value normal_price"}).find("span", {"class": "normal_price"}).get("data-price"))
                    #
                    #    imgs = listing.find("img")
                    #    img_small = imgs.get("src")
                    #    img_big = img_small + "dpx2x"
                    #    #Thread(target=print, args=str(name)).start()
                    #
                    #    task_list.append(orm.async_insert_listing(name=name, val=price, ref_small_image=img_small, ref_big_image=img_big, ref_gun=ref))
                    #await asyncio.gather(*task_list)
                    break
        except ClientConnectionError as err:
            print(pg, "Error occured", err)
            proxy = random.choice(PROXIES)
            #await asyncio.sleep(1)
        except ConnectionError as err:
            print(pg, "Connection error", err)
            proxy = random.choice(PROXIES)
            #await asyncio.sleep(1)
        except SerializationError as err:
            print(pg, "Serialization Error occured")
            await asyncio.sleep(1)
        except TypeError as err:
            print(pg, "Type Error occured", err)
            proxy = random.choice(PROXIES)
        except AttributeError as err:
            print(pg, "Attribute error", err)
            #await asyncio.sleep(1)
            #await asyncio.sleep(1)


            #loop.run_until_complete(task_list)


async def table_update(pages) -> None:#List[Coroutine | Any]:
    list_of_tasks = []
    #or await asyncio.sleep(0.5)
    #[await get_prices(i) for i in range(1, 4)]

    [await get_prices(i) for i in range(1, pages[0])]
    await get_prices(pages[0], pages[1])



    #[list_of_tasks.append(get_prices(i)) for i in range(1, pages[0])]
    #list_of_tasks.append(get_prices(pages[0], pages[1]))
    #await asyncio.gather(*list_of_tasks)










if __name__ == "__main__":
    start = time.time()
    loop = asyncio.get_event_loop()
    #pages = loop.run_until_complete(pagination_limit()) FOR POWERFUL DATABASE
    pages = (11, 0)
    loop.run_until_complete(table_update(pages))
    end = time.time()



