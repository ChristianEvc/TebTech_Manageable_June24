from langchain_core.output_parsers import StrOutputParser
from GraphComponents.llm_setup import create_retriever, llm_max, llm_mini, llm_mini_stream
from GraphComponents.prompts import followup_prompt, rag_prompt, question_for_rag, grade_prompt, source_prompt, question_category_prompt
from Utilities.markdownAndUpload import write_and_upload_markdown_content
from langchain_core.messages import AIMessage, HumanMessage
from Utilities.schemas import GradeDocuments, Source
from Utilities.pineconeNamespaces import get_namespaces


question_category_generator = question_category_prompt | llm_max | StrOutputParser()
single_question_gen = question_for_rag | llm_mini | StrOutputParser()

def continue_conversation(state):
    print("---NEW CONVO OR CONTINUATION---")
    try:
        question_category = state.get("question_category")
        print("question category: ", question_category)
        if question_category is None:
            return "new"
        elif question_category == "uncertain":
            return "new"
        else:
            return "continue"
    except AttributeError:
        # This handles the case where 'state' itself is None
        return "new"

def categorize_question(state):
    print("---CATEGORIZE---")
    messages = state["messages"]
    namespaces = get_namespaces()
    question_category = question_category_generator.invoke({"messages": messages, "namespaces": namespaces})
    return {"question_category": question_category, "namespaces": namespaces}

def singleQuestionGen(state):
    messages = state["messages"]
    single_question = single_question_gen.invoke(messages)
    return {"single_question": single_question}
       
def retriever(state):
    print("---RETRIEVE---")
    question_category = state["question_category"]
    messages = state["messages"]
    latest_question = messages[-1].content
    print("---LATEST QUESTION---")
    retriever = create_retriever(question_category)
    documents = retriever.invoke(latest_question)
    return {"documents": documents}

def followup(state):
    print("---FOLLOWUP---")
    messages = state["messages"]
    namespaces = state["namespaces"]
    followup_generator = followup_prompt | llm_mini | StrOutputParser()
    followup_question = followup_generator.invoke({"messages": messages, "namespaces": namespaces})
    return {"messages": followup_question}

def decide_to_rag(state):
    print("---DECIDE TO RAG---")
    q_category = state["question_category"]
    if q_category != 'uncertain':
        return "rag"
    else:
        return "followup"

def grade_documents(state):
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["single_question"]
    documents = state["documents"]
    structured_llm_grader = llm_mini.with_structured_output(GradeDocuments)
    retrieval_grader = grade_prompt | structured_llm_grader
    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question}

def generate(state):
    print("---GENERATE---")
    documents = state["documents"]
    messages = state["messages"]

    rag_chain = rag_prompt | llm_mini
    generation = rag_chain.invoke({"source_documents": documents, "messages": messages})
    print("--FULL GENERATION--")
    return {"generation": generation, "messages": generation}

def sourceHandling(state):
    print("--SOURCE--")
    documents = state["documents"]
    answer = state["generation"]
    source_llm_structured = llm_mini.with_structured_output(Source)
    source_chain = source_prompt | source_llm_structured
    source = source_chain.invoke({"context": documents, "answer": answer})
    return {"sourceData": source}

def loggingNode(state):
    print("---LOGGING---")
    markdown_content = "# LangChain Execution Log\n\n"

    # Log messages
    markdown_content += "## Messages\n"
    try:
        messages = state["messages"]
        for message in messages:
            markdown_content += f"- {message}\n"
    except KeyError:
        markdown_content += "No messages available.\n"
    markdown_content += "\n"

    # Log question category
    markdown_content += "## Question Category\n"
    try:
        question_category = state["question_category"]
        markdown_content += f"{question_category}\n"
    except KeyError:
        markdown_content += "Question category not available.\n"
    markdown_content += "\n"

    # Log single question
    markdown_content += "## Single Question\n"
    try:
        single_question = state["single_question"]
        markdown_content += f"{single_question}\n"
    except KeyError:
        markdown_content += "Single question not available.\n"
    markdown_content += "\n"

    # Log documents
    markdown_content += "## Retrieved Documents\n"
    try:
        documents = state["documents"]
        if documents:
            for i, doc in enumerate(documents, 1):
                markdown_content += f"### Document {i}\n"
                markdown_content += f"**Content:** {doc.page_content}\n"
                markdown_content += "**Metadata:**\n"
                for key, value in doc.metadata.items():
                    markdown_content += f"- {key}: {value}\n"
                markdown_content += "\n"
        else:
            markdown_content += "No documents retrieved.\n"
    except KeyError:
        markdown_content += "Documents not available.\n"
    markdown_content += "\n"

    # Log generation
    markdown_content += "## Generated Answer\n"
    try:
        generation = state["generation"]
        markdown_content += f"{generation}\n"
    except KeyError:
        markdown_content += "Generated answer not available.\n"
    markdown_content += "\n"

    # Log source data
    markdown_content += "## Source Data\n"
    try:
        source_data = state["sourceData"]
        markdown_content += f"{source_data}\n"
    except KeyError:
        markdown_content += "Source data not available.\n"
    markdown_content += "\n"

    # Log namespaces
    markdown_content += "## Namespaces\n"
    try:
        namespaces = state["namespaces"]
        for namespace in namespaces:
            markdown_content += f"- {namespace}\n"
    except KeyError:
        markdown_content += "Namespaces not available.\n"

    # Upload the markdown content
    write_and_upload_markdown_content(markdown_content, "Full_Graph_Run_")

    return {"loggingDone": True}