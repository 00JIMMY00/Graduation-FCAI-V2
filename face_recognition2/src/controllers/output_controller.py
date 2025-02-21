import json

async def combine_results(recognition_result, voice_result):
    """
    Combines the recognition result and voice result into the desired JSON format.
    """
    output = {
        "name": recognition_result.get("name"),
        "class": recognition_result.get("class"),
        "input": voice_result.get("text")
    }

    print("Combined Output:", output)
    return json.dumps(output)