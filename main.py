#!/usr/bin/env python3
"""Main entrypoint for the app."""
import logging
from typing import Optional
import asyncio
import traceback

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from langchain.pydantic_v1 import BaseModel
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain_core.messages import HumanMessage

from Utilities.schemas import ChatResponse, SourceResponse
from GraphComponents.workflow import create_graph
from Utilities.credentials import update_json_with_signed_url

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the input model to include both question and history
class QuestionInput(BaseModel):
    question: str
    history: str

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Starting backend")


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, userId: str = Query(...)):
    await websocket.accept()
    qa_chain = create_graph()

    while True:
        try:
            # Receive and send back the client message
            # Use asyncio.wait_for to apply a timeout to the receive_text() function
            question = await asyncio.wait_for(websocket.receive_text(), timeout=120)
            resp = ChatResponse(sender="you", message=question, type="stream")
            await websocket.send_json(resp.model_dump())
            print("Question:", question)

            # Construct a response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.model_dump())
            
            async for event in qa_chain.astream_events(
                {"messages": [HumanMessage(content=question)]},
                config={'callbacks': [ConsoleCallbackHandler()], "configurable": {"thread_id": userId}},
                version="v2",
            ):
                node = event.get('metadata', {}).get('langgraph_node', 'ignore')

                if event["event"] == "on_chat_model_stream" and ("generate" in node or "followup" in node):
                    token = event.get('data', {}).get('chunk', {}).content
                    resp = ChatResponse(sender="bot", message=token, type="stream")
                    await websocket.send_json(resp.model_dump())

                elif event["event"] == "on_chain_end" and "source" in node:
                    source_data = event.get('data', {}).get('output', {}).get('sourceData', {})
                    print("SourceData", event)
                    source_resp = SourceResponse(sender="bot", message=source_data, type="source")
                    await websocket.send_json(source_resp.model_dump())

                else:
                    continue

            end_resp = ChatResponse(sender="bot", message="", type="end")
            await websocket.send_json(end_resp.model_dump())
        
        except asyncio.TimeoutError:
            logging.info("websocket inactivity timeout")
            await websocket.close()
            break
        except WebSocketDisconnect:
            logging.info("websocket disconnect")
            break
        except Exception as e:
            tb = traceback.format_exc()  # This formats the traceback
            logging.error("An error occurred: %s", str(e))
            logging.error("Traceback: %s", tb)
            resp = ChatResponse(
                sender="bot",
                message="Sorry, something went wrong. Try again.",
                type="error",
            )
            await websocket.send_json(resp.model_dump())

@app.websocket("/reset")
async def websocket_reset_endpoint(websocket: WebSocket):
    try:
        # Accept the WebSocket Connection
        await websocket.accept()
      
        # Wait for any message from client (i.e. the empty JSON object sent upon `resetChat` execution)
        data = await websocket.receive_text()
      
        # Send success status to client
        await websocket.send_json({"status": "success"})

        # Close the websocket as soon as the job is done
        await websocket.close()

    except WebSocketDisconnect:
        logging.info("WebSocket reset disconnected")
        
    except Exception as e:
        tb = traceback.format_exc()
        logging.error("Exception during websocket reset: %s", str(e))
        logging.error("Traceback: %s", tb)
        await websocket.send_json({"status": "error", "message": str(e)})
        await websocket.close()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8080)
