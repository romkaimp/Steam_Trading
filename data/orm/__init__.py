from data.orm.async_orm import async_create_tables
import asyncio
import os



loop = asyncio.get_event_loop()
loop.run_until_complete(async_create_tables())