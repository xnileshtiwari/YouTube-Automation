import base64
import os
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()


def image_generator(instruction):
    client = genai.Client(
        api_key=os.environ.get("GOOGLE_API_KEY"),
    )

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"Please generate image based on this article {instruction}"),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.5,
        response_modalities=[
            "image",
            "text",
        ],
        
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_CIVIC_INTEGRITY",
                threshold="OFF",  # Off
            ),
        ],
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
            continue
        if chunk.candidates[0].content.parts[0].inline_data:
            file_name = "ENTER_FILE_NAME"
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            save_binary_file(
                f"{file_name}{file_extension}", inline_data.data
            )
            return(
                "File of mime type"
                f" {inline_data.mime_type} saved"
                f"to: {file_name}"
            )
        else:
            return(chunk.text)

res = image_generator("A beautiful sunset over the ocean")
print(res)