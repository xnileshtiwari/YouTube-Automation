import base64
import os
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv
from termcolor import colored
from langchain_core.messages import AIMessage, HumanMessage
from typing import Sequence
from typing_extensions import TypedDict
from libs.prompts import iamge_generator_prompt  


def get_last_article(messages):
    for msg in reversed(messages):
        if msg.type == "ai" and msg.content.startswith("Article:"):
            return msg.content[len("Article: "):].strip()
    return None

class State(TypedDict):
    messages: Sequence[AIMessage | HumanMessage]
    iteration: int

load_dotenv()

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)

def image_generator(instruction):
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=instruction)],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        temperature=0.8,
        system_instruction=[types.Part.from_text(text=iamge_generator_prompt)],
    )

    response = client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    
    full_text = ""
    for chunk in response:
        if chunk.text:
            full_text += chunk.text
    prompt = full_text
    print(colored("Prompt: " + prompt, "white", "on_green"))

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.5,
        response_modalities=["image", "text"],
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_CIVIC_INTEGRITY",
                threshold="OFF",
            ),
        ],
        response_mime_type="text/plain",
    )

    image_path = None
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
            continue
        if chunk.candidates[0].content.parts[0].inline_data:
            file_name = "Image"
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            full_file_name = f"{file_name}{file_extension}"
            save_binary_file(full_file_name, inline_data.data)
            image_path = full_file_name
            print(
                f"File of mime type {inline_data.mime_type} saved to: {full_file_name}"
            )
        else:
            print(chunk.text)
    return image_path  # Return the path or None if no image

async def image_generator_node(state: State) -> State:
    print(colored("Generating cover image...", "yellow"))
    article = get_last_article(state["messages"])
    if not article:
        raise ValueError("No article found in state")
    image_path = image_generator(article)
    if image_path:
        state["image_path"] = image_path  # Store path in state
    print(colored("Cover image generated.", "green"))
    return state