#import data.fake_data.fake_orm as fkorm
#from data.parser.parser import list_names_images
#import asyncio
#import time
#
#fkorm.delete_all()
#
#async def main() -> list:
#    task = asyncio.create_task(list_names_images(5))
#    return await task  # Дожидаемся завершения задачи
#
#if __name__ == "__main__":
#    zoom = asyncio.run(main())
#    fkorm.insert_all(zoom)