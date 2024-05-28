import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request, WebSocket, WebSocketDisconnect,HTTPException  
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.websockets import WebSocketState
# from llm import LlmClient
from llm_with_func_calling import LlmClient
from twilio_server import TwilioClient
from retellclient.models import operations,components
from twilio.twiml.voice_response import VoiceResponse
import asyncio
import retellclient
from staffagent_api import StaffAgentAPIClient
import uuid

STAFF_AGENT_API_URL = os.getenv('STAFF_AGENT_API_URL')

load_dotenv()

app = FastAPI()


twilio_client = TwilioClient()
staffagent_api = StaffAgentAPIClient(STAFF_AGENT_API_URL)


@app.post("/twilio-voice-webhook/{agent_id_path}")
async def handle_twilio_voice_webhook(request: Request, agent_id_path: str):
    sa_call_uuid = request.query_params.get("sa_call_uuid")
    print("inside twilio voice webhook")
    print(f"Query param sa_call_uuid: {sa_call_uuid}")
    print(f"Request URL: {request.url}")
    try:
        # Check if it is machine
        twilio_data = await request.form()
        print(twilio_data)
        caller = twilio_data.get('Caller')
        call_direction = twilio_data.get('Direction')
        if 'AnsweredBy' in twilio_data and twilio_data['AnsweredBy'] == "machine_start":
            twilio_client.end_call(twilio_data['CallSid'])
            return PlainTextResponse("")

        call_response = twilio_client.retell.register_call(operations.RegisterCallRequestBody(
            agent_id=agent_id_path, 
            audio_websocket_protocol="twilio",  # type: ignore
            audio_encoding="mulaw",  # type: ignore
            sample_rate=8000,
        ))
        print("===========Call Response")
        print(call_response)
        print("===========Call Response")
        if call_response.call_detail:     # type: ignore
            response = VoiceResponse()
            start = response.connect()
            start.stream(url=f"wss://api.retellai.com/audio-websocket/{call_response.call_detail.call_id}")  # type: ignore
            if sa_call_uuid is None and call_direction == "inbound":
                print("sa_call_uuid is None and call_direction is inbound")
                call_data = {
                    "status": "ringing",
                    "inbound": True,
                    "uuid": str(uuid.uuid4()),
                    "twilio_payload": dict(twilio_data),
                    "retell_call_id_ref": call_response.call_detail.call_id,
                    "retell_agent_id_ref": agent_id_path,
                }
                call = await staffagent_api.create_call(call_data)
                print(f"Created call: {call}")
            elif sa_call_uuid is not None and call_direction == "outbound-api":
                print("sa_call_uuid is not None and call_direction is outbound-api")
                attrs = {
                    "retell_call_id_ref": call_response.call_detail.call_id,
                    "status": twilio_data.get('CallStatus'),
                    "twilio_payload": dict(twilio_data)
                }
                print(f"Updating call with attrs: {attrs}")
                updated_call = staffagent_api.update_call(sa_call_uuid, attrs)
                print(f"Updated call: {updated_call}")
            
            return PlainTextResponse(str(response), media_type='text/xml')
        else:
            print("SOMETHING WENT WRONG")
            print(call_response)

    except Exception as err:
        print(f"Error in twilio voice webhook: {err}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

@app.websocket("/llm-websocket/{call_id}")
async def websocket_handler(websocket: WebSocket, call_id: str):
    await websocket.accept()
    print(f"===========Handle llm ws for: {call_id}")
    llm_client = LlmClient(call_id)

    # send first message to signal ready of server
    response_id = 0
    first_event = llm_client.draft_begin_messsage()
    print(f"beginSentence: {json.dumps(first_event)}")
    await websocket.send_text(json.dumps(first_event))

    async def stream_response(request):
        nonlocal response_id
        for event in llm_client.draft_response(request):
            await websocket.send_text(json.dumps(event))
            if request['response_id'] < response_id:
                return # new response needed, abondon this one
    try:
        while True:
            message = await websocket.receive_text()
            request = json.loads(message)
            # print out transcript
            os.system('cls' if os.name == 'nt' else 'clear')
            # print(json.dumps(request, indent=4))
            
            if 'response_id' not in request:
                continue # no response needed, process live transcript update if needed
            response_id = request['response_id']
            asyncio.create_task(stream_response(request))
    except WebSocketDisconnect:
        print(f"LLM WebSocket disconnected for {call_id}")
    except Exception as e:
        print(f'LLM WebSocket error for {call_id}: {e}')
    finally:
        print(f"LLM WebSocket connection closed for {call_id}")

