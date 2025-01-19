import asyncio
from face_recognition2 import RecognitionController
rc = RecognitionController()

async def main():
    # Create tasks for both functions
    task1 = asyncio.create_task(rc.start_recognition())
    task2 = asyncio.create_task(rc.get_recognition_result())

    # Wait for both tasks to complete
    await task1  # Ensure start_recognition completes
    result = await task2  # Get the result of get_recognition_result

    # Print or process the result
    print("Recognition Result:", result)

# Run the event loop
asyncio.run(main())
