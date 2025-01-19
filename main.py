# from face_recognition2 import RecognitionController
import asyncio
# from middle_ware import DataPipeline
from face_recognition2 import RecognitionController
import asyncio
rc = RecognitionController()
# rc.start_recognition()

# asyncio.run(print( await rc.get_recognition_result()))
# print(asyncio.run(rc.get_recognition_result()))


async def main():
    # await asyncio.gather(rc.start_recognition(), rc.get_recognition_result())
    # await rc.start_recognition()
    # await rc.get_recognition_result()
    # print("hello")
    task1 = asyncio.create_task(rc.start_recognition())
    task2 = asyncio.create_task(rc.get_recognition_result())
    task3 = asyncio.create_task(main2())
    print("hello1")
    await task1
    await task2
    await task3

async def main2():
    print("hello2")


asyncio.run(main())

