from libs.generative import llm
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from libs.prompts import crittic_prompt
from termcolor import colored
from typing import Sequence
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage
class State(TypedDict):
    messages: Sequence[AIMessage | HumanMessage]  
    iteration: int


critic_prompt = ChatPromptTemplate.from_messages([
    ("user", crittic_prompt),
    ("user", "Here is the article to review:\n{article}"),
])
critic_chain = critic_prompt | llm

def get_last_article(messages):
    for msg in reversed(messages):
        if msg.type == "ai" and msg.content.startswith("Article:"):
            return msg.content[len("Article: "):].strip()
    return None

async def critic_node(state: State) -> State:
    print(colored("Critiquing article...", "yellow"))
    article = get_last_article(state["messages"])
    if not article:
        raise ValueError("No article found in state")
    critique = await critic_chain.ainvoke({"article": article})
    critique_text = critique.content if hasattr(critique, 'content') else str(critique)
    print(colored(f"Critique: {critique_text}", "white", "on_blue"))
    print(colored("Critique generated.", "green"))
    msg = HumanMessage(content=f"Critique: {critique_text}")
    msg.role = "user"  # set valid role for Gemini
    return {
        "messages": state["messages"] + [msg],
        "iteration": state["iteration"] + 1
    }
