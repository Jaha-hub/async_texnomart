import asyncio

async def task(name,delay):
    print(f"Задача {name} запустилась")
    await asyncio.sleep(delay)
    print(f"Задача {name} выполнена")
if __name__ == "__main__":
    asyncio.run(task("Отжимания", 3))