from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from staffagent_api import StaffAgentAPIClient
STAFF_AGENT_API_URL = os.getenv('STAFF_AGENT_API_URL')
staffagent_api = StaffAgentAPIClient(STAFF_AGENT_API_URL)

load_dotenv()


class LlmClient:
    def __init__(self, retell_call_id):
        self.client = OpenAI(
            organization=os.environ['OPENAI_ORGANIZATION_ID'],
            api_key=os.environ['OPENAI_API_KEY'],
        )
        self.retell_call_id = retell_call_id
        self.beginSentence, self.agentPrompt = self.get_staff_agent_api_data()

    def get_staff_agent_api_data(self):
        call_response = staffagent_api.get_call_prompt(self.retell_call_id)
        print("Got prompt from staffagent phone agent")
        print(call_response)
        return call_response["greeting"], call_response["prompt"]

    def draft_begin_messsage(self):
        return {
            "response_id": 0,
            "content": self.beginSentence,
            "content_complete": True,
            "end_call": False,
        }
    
    def convert_transcript_to_openai_messages(self, transcript):
        messages = []
        for utterance in transcript:
            if utterance["role"] == "agent":
                messages.append({
                    "role": "assistant",
                    "content": utterance['content']
                })
            else:
                messages.append({
                    "role": "user",
                    "content": utterance['content']
                })
        return messages

    def prepare_prompt(self, request):
        prompt = [{
            "role": "system",
            "content": self.agentPrompt
        }]
        transcript_messages = self.convert_transcript_to_openai_messages(request['transcript'])
        for message in transcript_messages:
            prompt.append(message)

        if request['interaction_type'] == "reminder_required":
            prompt.append({
                "role": "user",
                "content": "(Now the user has not responded in a while, you would say:)",
            })
        return prompt

    # Step 1: Prepare the function calling definition to the prompt
    def prepare_functions(self):
        functions= [
            {
                "type": "function",
                "function": {
                    "name": "end_call",
                    "description": "End the call only when user explicitly requests it.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message you will say before ending the call with the customer.",
                            },
                        },
                        "required": ["message"],
                    },
                },
            },
        ]
        return functions
    
    def draft_response(self, request):      
        prompt = self.prepare_prompt(request)
        func_call = {}
        func_arguments = ""
        stream = self.client.chat.completions.create(
            model="gpt-4",   # type: ignore
            # model="gpt-3.5-turbo-1106",   # type: ignore
            messages=prompt,                # type: ignore
            stream=True,
            # Step 2: Add the function into your request
            tools=self.prepare_functions()      # type: ignore
        )
    
        for chunk in stream:
            # Step 3: Extract the functions
            if chunk.choices[0].delta.tool_calls:
                tool_calls = chunk.choices[0].delta.tool_calls[0]
                if tool_calls.id:
                    if func_call:
                        # Another function received, old function complete, can break here.
                        break
                    func_call = {
                        "id": tool_calls.id,
                        "func_name": tool_calls.function.name or "",
                        "arguments": {},
                    }
                else:
                    # append argument
                    func_arguments += tool_calls.function.arguments or ""
            
            # Parse transcripts
            if chunk.choices[0].delta.content:
                yield {
                    "response_id": request['response_id'],
                    "content": chunk.choices[0].delta.content,
                    "content_complete": False,
                    "end_call": False,
                }
        
        # Step 4: Call the functions
        if func_call:
            if func_call['func_name'] == "end_call":
                func_call['arguments'] = json.loads(func_arguments)
                yield {
                    "response_id": request['response_id'],
                    "content": func_call['arguments']['message'],
                    "content_complete": True,
                    "end_call": True,
                }
            # Step 5: Other functions here
        else:
            # No functions, complete response
            yield {
                "response_id": request['response_id'],
                "content": "",
                "content_complete": True,
                "end_call": False,
            }