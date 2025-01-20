import asyncio

async def boil_water():
    print("Starting to boil water...")
    await asyncio.sleep(3)  # Simulates a 3-second wait for boiling water
    print("Water boiled!")

async def make_sandwich():
    print("Making a sandwich...")
    await asyncio.sleep(1)  # Simulates a 1-second task
    print("Sandwich ready!")

async def main():
    # Run both tasks concurrently
    await asyncio.gather(boil_water(), make_sandwich())

# Run the event loop
asyncio.run(main())
