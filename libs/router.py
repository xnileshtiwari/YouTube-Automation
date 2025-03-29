from dotenv import load_dotenv
from typing import Sequence
from langchain_core.messages import AIMessage, HumanMessage
from typing_extensions import TypedDict
from termcolor import colored




class State(TypedDict):
    messages: Sequence[AIMessage | HumanMessage]
    iteration: int
    image_path: str  # Added to store image path



def route_after_critic(state: State) -> str:
    last_critique = state["messages"][-1].content
    if "NEXT" in last_critique or state["iteration"] >= 3:
        print(colored("Critic satisfied or max iterations reached. Moving to image generation.", "cyan"))
        return "image_generator"
    print(colored("Critic suggests improvements. Returning to writer.", "cyan"))
    return "writer"
