import asyncio
from face_recognition2 import RecognitionController
rc = RecognitionController()

async def main():
    # Create tasks for both functions
    task1 = asyncio.create_task(rc.start_recognition())
    task2 = asyncio.create_task(main2())

    # await asyncio.gather(task1, task2)
    await task1  # Ensure start_recognition completes
    await task2  # Get the result of get_recognition_result


async def main2():
    print(await rc.get_recognition_result())


# Run the event loop
asyncio.run(main())
