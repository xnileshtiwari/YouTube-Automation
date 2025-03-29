import streamlit as st
import asyncio
import time
from langchain_core.messages import HumanMessage
from typing import Sequence
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from libs.critic import critic_node
from libs.writter import writer_node  
from libs.title_generator import title_generator_node
from libs.image_gen import image_generator_node
from libs.notion import save_node
from libs.router import route_after_critic

class State(TypedDict):
    messages: Sequence[HumanMessage]
    iteration: int
    image_path: str
    saved: bool

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

def save_node(state: State) -> State:
    state["saved"] = True
    return state

async def generate_article(thread_id: str) -> bool:
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "messages": [HumanMessage(content="Generate a title for a Medium story")],
        "iteration": 0,
        "saved": False
    }
    final_state = initial_state
    async for state in graph.astream(initial_state, config):
        final_state = state
    return final_state.get("saved", False)

async def generate_five_articles() -> list[bool]:
    results = []
    for i in range(5):
        result = await generate_article(f"article_{i}")
        results.append(result)
    return results

st.title("Article Generator")
st.write("App loaded, waiting for button press.")
if st.button("Generate 5 Articles", type="primary"):
    st.write("Button pressed, starting generation.")
    st.write("Starting article generation...")
    start_time = time.time()
    results = asyncio.run(generate_five_articles())
    end_time = time.time()
    successful = sum(results)
    total_time = end_time - start_time
    st.write(f"Successfully generated {successful} out of 5 articles in {total_time:.2f} seconds")
    if successful < 5:
        st.write(f"Failed to generate {5 - successful} articles")
