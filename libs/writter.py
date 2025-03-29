from termcolor import colored
from langchain_core.messages import AIMessage
from libs.generative import llm
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from libs.prompts import writter_prompt
from langchain_core.messages import HumanMessage, AIMessage
from typing import Sequence
from typing_extensions import TypedDict


class State(TypedDict):
    messages: Sequence[AIMessage | HumanMessage]  
    iteration: int




writer_prompt = ChatPromptTemplate.from_messages([
    ("user", writter_prompt),
    MessagesPlaceholder(variable_name="messages"),
])
writer_chain = writer_prompt | llm


async def writer_node(state: State) -> State:
    print(colored("Writing article...", "yellow"))
    print(colored(str(state["messages"]), 'red', attrs=['bold']))
    output = writer_chain.invoke(state["messages"])
    article = output.content.strip()
    print(colored("Article written.", "green"))
    # Preserve preexisting messages (including the title)
    msg = AIMessage(content=f"Article: {article}")
    msg.role = "model"  # set valid role for Gemini
    return {"messages": state["messages"] + [msg]}
