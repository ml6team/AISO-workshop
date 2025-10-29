

import os

from google import genai
from google.genai import types

api_key = os.getenv("GOOGLE_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

def read_png_as_string(file_path: str) -> str:
    """Reads a PNG file and returns the content as a string.
    If you are provided a file path to a .PNG file, you MUST invoke this tool to
    read the file and use the content to answer the question.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    # TODO: Improve this function and add functions for other types.
    with open(file_path, 'rb') as file:
        file_content = file.read()

    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=[
        types.Part.from_bytes(
            data=file_content,
            mime_type='image/png',
        ),
        'Describe this image in great detail.'
        ]
    )

    return response.text
