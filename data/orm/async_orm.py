import datetime
import os
import pickle
import asyncio
import numpy as np
import pandas
import pandas as pd
from asyncpg.exceptions import SerializationError
from data.orm.engine import async_engine, async_session, Base
from data.orm.models import metadata_obj, SteamListings
from sqlalchemy import select, func, and_, update, insert

NEW_VAL_COUNT = 30


async def async_create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        #await metadata_obj.create_all(async_engine)


async def async_drop_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def async_select_pk_refs():
    async with async_session() as session:
        query = select(SteamListings.name, SteamListings.ref)
        result = await session.execute(query)
        #print(f"{result.all()=}")
        return result.all()


async def async_select_all(n: int | None = None, names: bool=False):
    async with async_session() as session:
        if names:
            if n is None:
                query = select(SteamListings.name).limit(10)
            else:
                query = select(SteamListings.name).limit(n)
            result = await session.execute(query)
            return result.scalars().all()
        if n is None:
            query = select(SteamListings).limit(10)
        else:
            query = select(SteamListings).limit(n)
        result = await session.execute(query)
        #print(result.scalars().all())
        return result.scalars().all()


async def async_select_ts(name) -> pandas.DataFrame | None:
    async with async_session() as session:
        query = select(SteamListings.time_series_pckl).filter_by(name=name)
        result = await session.execute(query)
        if len(time_serial := result.scalars().all()) != 0:
            df: pandas.DataFrame = pickle.loads(time_serial[0])
            #print(df)
            return df
        return None


async def async_find_by_name(name):
    async with async_session() as session:
        query = select(SteamListings).filter_by(name=name)
        result = await session.execute(query)
        return result.scalars().all()
        #print(f"{result.scalars().all()=}")


async def async_ml_weights_values(name):
    async with async_session() as session:

        query2 = select(SteamListings.time_series_new_val).filter_by(name=name)
        res2 = await session.execute(query2)
        query1 = select(SteamListings.ml_weights).filter_by(name=name)
        res1 = await session.execute(query1)
        return res1.scalars().all()[0], res2.scalars().all()[0]


async def async_update_weight(name, weights):
    async with async_session() as session:
        query_get_new_val_number = select(SteamListings.time_series_new_val).filter_by(name=name)
        res_new_val_number = (await session.execute(query_get_new_val_number)).scalars().all()[0] - NEW_VAL_COUNT

        query = (update(SteamListings).
                 values(time_series_pckl=weights, time_series_new_val=res_new_val_number).
                 filter_by(name=name))
        await session.execute(query)
        await session.commit()


async def async_check_contains(name) -> bool:
    async with async_session() as session:
        name = name
        query1 = select(SteamListings).filter_by(name=name)
        if len((await session.execute(query1)).all()) == 0:
            return True
        else:
            return False


async def async_insert_listing(name, val=0, ref_small_image = '', ref_big_image = '', ref_gun = '', date: datetime = datetime.datetime.now()):
    async with async_session() as session:
        while True:
            try:
                a = pickle.dumps(pd.DataFrame({"cost": [val], "time": [date]}, ))
                query1 = select(SteamListings).filter_by(name=name)
                if len((await session.execute(query1)).all()) == 0:
                    query = insert(SteamListings).values(name=name, main_gun=name, time_series_pckl=a,
                                                         image_small=ref_small_image, image_big=ref_big_image,
                                                         ref=ref_gun, time_series_new_val=1)
                    #new_item = SteamListings(name=name, main_gun=name, time_series_pckl=a, ref="")
                    await session.execute(query)
                else:
                    #await async_update_ts(name, val, date)
                    query_get = select(SteamListings.time_series_pckl).filter_by(name=name)
                    res = (await session.execute(query_get)).scalars().all()

                    query_get_new_val_number = select(SteamListings.time_series_new_val).filter_by(name=name)
                    res_new_val_number = (await session.execute(query_get_new_val_number)).scalars().all()[0]

                    if len(res) == 0:
                        return await async_insert_listing(name=name, val=val, date=date)
                    res = pickle.loads(res[0])
                    res_new_val_number += 1

                    if res.size >= SteamListings.ts_long:
                        res = res.loc[1:]
                    res.loc[len(res.index)] = [val, date]
                    pckl = pickle.dumps(res)

                    query_update = (update(SteamListings)
                                    .values(time_series_pckl=pckl, time_series_new_val=res_new_val_number)
                                    .filter_by(name=name))

                    await session.execute(query_update)

                await session.commit()
                break
            except SerializationError as err:
                await asyncio.sleep(1)


#async def async_insert_new_val(*args):
#    async with async_session() as session:
#        name = args[0]
#        query1 = select(SteamListings).filter_by(name=name)
#        if len((await session.execute(query1)).all()) == 0:
#            new_item = SteamListings(name=args[0], main_gun=args[1], time_series_pckl=pickle.dumps(args[2]), ref=args[3])
#            session.add(new_item)
#        session.commit()
async def async_update_ts(name, val, date=datetime.datetime.now()):
    async with async_session() as session:

        query_get = select(SteamListings.time_series_pckl).filter_by(name=name)
        res = (await session.execute(query_get)).scalars().all()
        print(pickle.loads(res[0]))

        query_get_new_val_number = select(SteamListings.time_series_new_val).filter_by(name=name)
        res_new_val_number = (await session.execute(query_get_new_val_number)).scalars().all()[0]

        if len(res) == 0:
            return await async_insert_listing(name=name, val=val, date=date)
        res = pickle.loads(res[0])
        res_new_val_number += 1

        if res.size >= SteamListings.ts_long:
            res = res.loc[1:]
        res.loc[len(res.index)] = [val, date]
        pckl = pickle.dumps(res)

        query_update = (update(SteamListings)
                        .values(time_series_pckl=pckl, time_series_new_val=res_new_val_number)
                        .filter_by(name=name))

        await session.execute(query_update)
        await session.commit()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    #loop.run_until_complete(async_drop_tables())
    #print(loop.run_until_complete(async_select_ts("Kilowatt Case")))
    #print(loop.run_until_complete(async_find_by_name("Kilowatt Case")))
    print(loop.run_until_complete(async_select_all(names=True)))

