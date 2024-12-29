from GraphComponents.state_definitions import AgentState
from GraphComponents.node_functions import categorize_question, generate, decide_to_rag, followup, retriever, sourceHandling, loggingNode, continue_conversation, singleQuestionGen
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver



def create_graph():
    memory = AsyncSqliteSaver.from_conn_string(":memory:")
    
    workflow = StateGraph(AgentState)

    workflow.add_node("categorize", categorize_question)
    workflow.add_node("followup", followup)
    workflow.add_node("retriever", retriever)
    #workflow.add_node("grade_documents", grade_documents)  # grade documents
    workflow.add_node("generate", generate)
    workflow.add_node("source", sourceHandling)
    workflow.add_node("logging", loggingNode)
    
    #workflow.add_node("grade_documents", grade_documents)

    #workflow.set_entry_point("continue_conversation")
    workflow.add_conditional_edges(
        START,
        continue_conversation,
        {
            "continue": "generate",
            "new": "categorize",
        },
    )
    workflow.add_conditional_edges(
    "categorize",
    decide_to_rag,
    {
        "rag": "retriever",
        "followup": "followup",
    },
)
    #workflow.add_edge("retriever", "grade_documents")
    #workflow.add_edge("grade_documents", "generate")
    workflow.add_edge("retriever", "generate")
    workflow.add_edge("followup", "logging")
    workflow.add_edge("generate", "source")
    workflow.add_edge("source", "logging")
    workflow.add_edge("logging", END)

    graph = workflow.compile(checkpointer=memory)

    return graph