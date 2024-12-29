from typing import Annotated, Sequence, TypedDict, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    question_category: str
    documents: List[str]
    single_question: str
    generation: str
    sourceData: str
    namespaces: List[str]
    loggingDone: bool