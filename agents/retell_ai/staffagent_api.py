import os
import requests
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
import httpx
load_dotenv()

STAFF_AGENT_API_URL = os.getenv('STAFF_AGENT_API_URL')

class Call(BaseModel):
    id: int
    status: Optional[str] = None
    inbound: bool = True
    uuid: Optional[str] = None
    retell_call_id_ref: Optional[str] = None
    twilio_call_sid_ref: Optional[str] = None
    opp_phone_num: Optional[str] = None
    call_duration: Optional[int] = None
    job_application_id: Optional[int] = None
    initiated_by_id: Optional[int] = None
    phone_agent_id: Optional[int] = None
    class Config:
        extra = "allow"


class StaffAgentAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.endpoints = {
            'list_calls': '/calls',
            'create_call': '/calls',
            'get_call': '/calls/{call_id}',
            'update_call': '/calls/{call_id}',
            'get_call_context': '/call-context/{call_id}',
        }

    def get_calls(self):
        response = requests.get(f"{self.base_url}{self.endpoints['list_calls']}")
        return [Call(**call) for call in response.json()['data'] if isinstance(call, dict)]

    def get_call(self, call_id):
        endpoint = self.endpoints['get_call'].format(call_id=call_id)
        response = requests.get(f"{self.base_url}{endpoint}")
        return Call(**response.json()['data'])

    # async def update_call(self, call_id, data):
    #     endpoint = self.endpoints['update_call'].format(call_id=call_id)
    #     async with httpx.AsyncClient() as client:
    #         response = await client.put(f"{self.base_url}{endpoint}", json=data)
    #         print("Updating call.......data from Ex is")
    #         print(response.json())
    #         return Call(**response.json()['data'])

    def update_call(self, call_id, data):
        print("Updating call")
        print(data)
        endpoint = self.endpoints['update_call'].format(call_id=call_id)
        response = requests.put(f"{self.base_url}{endpoint}", json=data)
        print(response.json())
        return Call(**response.json()['data'])

    async def create_call(self, data):
        endpoint = self.endpoints['create_call']
        print("Creating call.........")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}{endpoint}", json=data)
            print(response)
            print(response.json())
            return Call(**response.json()['data'])


    def get_call_prompt(self, call_id):
        endpoint = self.endpoints['get_call_context'].format(call_id=call_id)
        response = requests.get(f"{self.base_url}{endpoint}")
        return response.json()['data']

staff_agent_api_client = StaffAgentAPIClient(STAFF_AGENT_API_URL)

