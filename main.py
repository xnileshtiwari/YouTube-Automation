# Import necessary libraries
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from termcolor import colored
import os
import shutil
from datetime import datetime

# Import provided agents
from title_generator import title_generator
from writter import writter_agent  # Assuming typo in 'writter'
from image_gen import image_generator



# Initialize the language model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
    verbose=True  # Enable verbose output
)

# Define the Writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a writer creating engaging Medium stories. Write the best article possible based on the given title. If critiques are provided, revise the article accordingly."),
    MessagesPlaceholder(variable_name="messages"),
])
writer_chain = writer_prompt | llm

# Define the Critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a critic reviewing a Medium story. Provide detailed feedback and suggestions for improvement. If the article is satisfactory, include 'NEXT' in your response."),
    ("human", "Here is the article to review:\n{article}"),
])
critic_chain = critic_prompt | llm

# Define the state
class State(TypedDict):
    messages: Sequence[AIMessage | HumanMessage]  
    iteration: int

# Helper function to extract the latest article
def get_last_article(messages):
    for msg in reversed(messages):
        if msg.type == "ai" and msg.content.startswith("Article:"):
            return msg.content[len("Article: "):].strip()
    return None

# Node definitions
async def title_generator_node(state: State) -> State:
    print(colored("Generating title...", "yellow"))
    title = title_generator()  # Call the provided title generator
    print(colored(f"Title generated: {title}", "green"))
    return {"messages": [AIMessage(content=f"Title: {title}")]}

async def writer_node(state: State) -> State:
    print(colored("Writing article...", "yellow"))
    print(colored(str(state["messages"]), 'red', attrs=['bold']))
    output = await writer_chain.ainvoke(state["messages"])
    article = output.content.strip()
    print(colored("Article written.", "green"))
    # Preserve preexisting messages (including the title)
    return {"messages": state["messages"] + [AIMessage(content=f"Article: {article}")]}

async def critic_node(state: State) -> State:
    print(colored("Critiquing article...", "yellow"))
    article = get_last_article(state["messages"])
    if not article:
        raise ValueError("No article found in state")
    critique = await critic_chain.ainvoke({"article": article})
    print(colored("Critique generated.", "green"))
    return {
        "messages": state["messages"] + [HumanMessage(content=f"Critique: {critique.content}")],
        "iteration": state["iteration"] + 1
    }

async def image_generator_node(state: State) -> State:
    print(colored("Generating cover image...", "yellow"))
    article = get_last_article(state["messages"])
    if not article:
        raise ValueError("No article found in state")
    image_generator(article)  # call function; ignore any returned image path
    print(colored("Cover image generated.", "green"))
    return state

async def save_node(state: State) -> State:
    print(colored("Saving article...", "yellow"))
    
    # Extract title
    title_msg = next((msg for msg in state["messages"] if msg.content.startswith("Title:")), None)
    if not title_msg:
        raise ValueError("Title not found")
    title = title_msg.content[len("Title: "):].strip()
    
    # Extract article
    article = get_last_article(state["messages"])
    if not article:
        raise ValueError("Article not found")
    
    # Create a new folder
    folder_name = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(folder_name, exist_ok=True)
    
    # Save markdown file without cover image
    md_content = f"# {title}\n\n{article}"
    md_path = os.path.join(folder_name, "article.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(colored(f"Article saved to {md_path}", "green"))
    return {}

# Conditional routing after critic
def route_after_critic(state: State) -> str:
    last_critique = state["messages"][-1].content
    if "NEXT" in last_critique or state["iteration"] >= 3:
        print(colored("Critic satisfied or max iterations reached. Moving to image generation.", "cyan"))
        return "image_generator"
    print(colored("Critic suggests improvements. Returning to writer.", "cyan"))
    return "writer"

# Build the graph
builder = StateGraph(State)
builder.add_node("title_generator", title_generator_node)
builder.add_node("writer", writer_node)
builder.add_node("critic", critic_node)
builder.add_node("image_generator", image_generator_node)
builder.add_node("save", save_node)

# Define edges
builder.add_edge(START, "title_generator")
builder.add_edge("title_generator", "writer")
builder.add_edge("writer", "critic")
builder.add_conditional_edges("critic", route_after_critic, {
    "writer": "writer",
    "image_generator": "image_generator"
})
builder.add_edge("image_generator", "save")
builder.add_edge("save", END)

# Compile the graph with memory
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# Run the graph
async def main():
    config = {"configurable": {"thread_id": "1"}}
    initial_state = {
        "messages": [HumanMessage(content="Generate a title for a Medium story")],
        "iteration": 0
    }
    print(colored("Starting the story generation process...", "magenta"))
    async for event in graph.astream(initial_state, config):
        print(event)
        print(colored("---", "blue"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())