import asyncpg
from asyncpg import Connection
from asyncio import get_event_loop

loop = get_event_loop()
async def get_db():
    #conn: Connection = await asyncpg.connect(user='postgres', password='Vfvekz196!', host='localhost')
    'postgresql://postgres@localhost/test'
    conn: Connection = await asyncpg.connect()
    async with conn.transaction():
        await conn.execute("CREATE TABLE if not exists dropper("
                       "id SERIAL PRIMARY KEY,"
                       "st VARCHAR(255)"
                       ");")
        await conn.execute("INSERT INTO dropper(st) VALUES ('SERIY')")
    print(await conn.fetch("SELECT * FROM dropper"))
    return conn

async def execute(conn):
    await conn.execute()

a = loop.run_until_complete(get_db())
print(a)