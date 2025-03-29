from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from typing import Sequence
from typing_extensions import TypedDict
from termcolor import colored
import os
from libs.critic import critic_node
from libs.writter import writer_node  
from libs.title_generator import title_generator_node
from libs.image_gen import image_generator_node
from libs.notion import save_node
from libs.router import route_after_critic

class State(TypedDict):
    messages: Sequence[AIMessage | HumanMessage]
    iteration: int
    image_path: str  # Added to store image path

# Build the graph
builder = StateGraph(State)
builder.add_node("title_generator", title_generator_node)
builder.add_node("writer", writer_node)
builder.add_node("critic", critic_node)
builder.add_node("image_generator", image_generator_node)
builder.add_node("save", save_node)
builder.add_edge(START, "title_generator")
builder.add_edge("title_generator", "writer")
builder.add_edge("writer", "critic")
builder.add_conditional_edges("critic", route_after_critic, {
    "writer": "writer",
    "image_generator": "image_generator"
})
builder.add_edge("image_generator", "save")
builder.add_edge("save", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

async def main():
    config = {"configurable": {"thread_id": "1"}}
    initial_state = {
        "messages": [HumanMessage(content="Generate a title for a Medium story")],
        "iteration": 0
    }
    initial_state["messages"][0].role = "user"
    print(colored("Starting the story generation process...", "magenta"))
    async for event in graph.astream(initial_state, config):
        print(event)
        print(colored("---", "blue"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())