import asyncio

async def test():
    print("Hello, world!")
    await asyncio.sleep(1)
    print("Goodbye, world!")

async def test2():
    print("Hello, world again!")
    await asyncio.sleep(1)
    print("Goodbye, world again!")

async def main():
    await asyncio.gather(test(), test2())

if __name__ == "__main__":
    asyncio.run(test())
    asyncio.run(test2())
