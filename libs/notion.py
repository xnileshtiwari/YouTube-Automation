from typing_extensions import TypedDict
from termcolor import colored
import os
import base64
import requests
from dotenv import load_dotenv
from typing import Sequence
from langchain_core.messages import AIMessage, HumanMessage



class State(TypedDict):
    messages: Sequence[AIMessage | HumanMessage]
    iteration: int
    image_path: str  # Added to store image path



load_dotenv()
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
PARENT_PAGE_ID = os.getenv("PARENT_PAGE_ID")
NOTION_VERSION = os.getenv("NOTION_VERSION")


def get_last_article(messages):
    for msg in reversed(messages):
        if msg.type == "ai" and msg.content.startswith("Article:"):
            return msg.content[len("Article: "):].strip()
    return None


def upload_to_imgbb(image_path, api_key):
    """Upload image to ImgBB and return the public URL."""
    url = "https://api.imgbb.com/1/upload"
    try:
        with open(image_path, "rb") as file:
            payload = {
                "key": api_key,
                "image": base64.b64encode(file.read()).decode('utf-8'),
            }
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                return response.json()["data"]["url"]
            else:
                print(colored(f"Image upload failed: {response.text}", "red"))
                return None
    except Exception as e:
        print(colored(f"Error uploading image: {e}", "red"))
        return None


async def save_node(state: State) -> State:
    print(colored("Saving article to Notion...", "yellow"))
    
    # Extract title
    title_msg = next((msg for msg in state["messages"] if msg.content.startswith("Title:")), None)
    if not title_msg:
        raise ValueError("Title not found")
    title = title_msg.content[len("Title: "):].strip()
    
    # Extract article
    article = get_last_article(state["messages"])
    if not article:
        raise ValueError("Article not found")
    
    # Handle image
    image_url = None
    image_path = state.get("image_path")
    if image_path and IMGBB_API_KEY:
        image_url = upload_to_imgbb(image_path, IMGBB_API_KEY)
        if not image_url:
            print(colored("Proceeding without image due to upload failure.", "yellow"))
    
    # Prepare Notion page data
    page_data = {
        "parent": {"page_id": PARENT_PAGE_ID},
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        },
        "children": []
    }
    
    # Add image block if available
    if image_url:
        page_data["children"].append({
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": image_url
                }
            }
        })
    
    # Add article content as paragraphs
    paragraphs = article.split("\n")
    for para in paragraphs:
        if para.strip():
            page_data["children"].append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": para.strip()
                            }
                        }
                    ]
                }
            })
    
    # Create Notion page
    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }
    create_page_url = "https://api.notion.com/v1/pages"
    response = requests.post(create_page_url, headers=headers, json=page_data)
    
    if response.status_code == 200:
        new_page_id = response.json()["id"]
        print(colored(f"Article saved to Notion page ID: {new_page_id}", "green"))
    else:
        print(colored(f"Failed to save to Notion: {response.text}", "red"))
    
    return {}
