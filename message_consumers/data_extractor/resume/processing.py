import asyncio
import os

import openai
from models.dynamic_schema import DynamicSchemaCreator
# from schemas.fields_data import fields_data
from openai import OpenAI
from instructor import patch
import instructor
from pydantic import ValidationError, BaseModel
from langsmith.wrappers import wrap_openai
import json
from langsmith import RunTree, traceable
import logging
from openai import AsyncOpenAI
from mistralai.client import MistralClient
import cohere
from langfuse.decorators import langfuse_context, observe
from langfuse import Langfuse


 




logging.basicConfig(level=logging.INFO)


class ResumeProcessor:
    def __init__(self, openai_api_key, data_schema, user_id):
        self.openai_client = instructor.patch(
            wrap_openai(OpenAI(api_key=openai_api_key)))
        self.data_schema = data_schema
        self.user_id  = user_id
        self.model_functions = {
            "gpt-4o-mini": self.process_resume_openai,
            "mistralai/Mixtral-8x7B-Instruct-v0.1": self.process_resume_together,
            "mistralai/Mixtral-8x22B-Instruct-v0.1": self.process_resume_anyscale

        }
        self.langfuse = Langfuse()
    
    @observe()
    async def process_resume(self, text, model_name, fallback_model):
        print(model_name)
        print("\n")
        process_function = self.model_functions.get(model_name)
        if process_function:
            return await process_function(text, model_name, fallback_model)
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        


    @observe()
    def fn(self):
        langfuse_context.update_current_trace(
                # session_id="15345",
                user_id=self.user_id,
                tags=["Resume-Extractor"]
        )


    @traceable(run_type="llm", name="process_resume", project_name="Data-Extractor")
    @observe()
    async def process_resume_openai(self, text, model_name, fallback_model):        

        self.fn()
        
        fields_data = self.data_schema

        # self.langfuse.create_prompt(
        #     name="resume-processing",
        #     type="chat",
        #     prompt=[{"role": "system", "content": "Please extract all the information from the given resume text and return it in the specified JSON format according to this schema: {{schema}}"}],
        #     labels=["production"],
        #     config={
        #         "model": "gpt-4o-mini",
        #         "temperature": 0.7,
        #         "supported_languages": ["en"]
        #     }
        # )
        

        # prompt_template = self.langfuse.get_prompt("resume-processing")
        # compiled_prompt = prompt_template.compile(schema=fields_data)

        prompt = f"""Please extract all the information from the given resume text and return it in the specified JSON format:

        Resume Text:
        {text}

        Structured Information (in JSON format):
        """

        GeneratedSchema = DynamicSchemaCreator.create_dynamic_schema(
            fields_data)

        rt = RunTree(
            run_type="llm",
            name="OpenAI Call RunTree",
            inputs={"messages": [
                {"role": "system", "content": "You are an AI assistant that extracts structured information from resumes."},
                {"role": "user", "content": prompt}
            ]},
            project_name="Data-Extractor"
        )

        try:
            response = self.openai_client.chat.completions.create(  # type:ignore
                model=model_name,  # Use the provided model name
                messages=[
                    {"role": "system", "content": "You are an AI assistant that extracts structured information from resumes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                n=1,
                stop=None,
                temperature=0,
                response_model=GeneratedSchema
            )
            
            

        except Exception as e:
            print(f"Error with model {model_name}: {str(e)}")
            print(f"Retrying with fallback model: {fallback_model}")

            response = self.openai_client.chat.completions.create(  # type:ignore
                model=fallback_model,  # Use the fallback model
                messages=[
                    {"role": "system", "content": "You are an AI assistant that extracts structured information from resumes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                n=1,
                stop=None,
                temperature=0,
                response_model=GeneratedSchema
            )

        structured_info = response

        if structured_info:
            try:
                structured_info_dict = structured_info.dict()
                rt.end(outputs=structured_info_dict)
                rt.post()
                return (json.dumps(structured_info_dict, indent=2))
            except ValidationError as e:
                print(f"Validation Error: {str(e)}")
                error_messages = []
                for error in e.errors():
                    field = error["loc"][0]
                    message = error["msg"]
                    error_messages.append(f"{field}: {message}")

                rt.end(outputs={"errors": error_messages})
                rt.post()
                return json.dumps({"errors": error_messages}, indent=2)
        else:
            rt.end(outputs=None)
            rt.post()
            return None

    @traceable(run_type="llm", name="process_resume_together", project_name="Data-Extractor")
    @observe()
    async def process_resume_together(self, text, model_name, fallback_model):

        print("Inside together LLM model now ")

        client = openai.OpenAI(
            base_url="https://api.together.xyz/v1",
            api_key=os.environ["TOGETHER_API_KEY"],
        )

        client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)

        fields_data = self.data_schema

        prompt = f"""Please extract all the information from the given resume text and return it in the specified JSON format:

        Resume Text:
        {text}

        Structured Information (in JSON format):
        """

        GeneratedSchema = DynamicSchemaCreator.create_dynamic_schema(
            fields_data)

        rt = RunTree(
            run_type="llm",
            name="Together Compute Call RunTree",
            inputs={"messages": [
                {"role": "user", "content": prompt}
            ]},
            project_name="Data-Extractor"
        )

        try:
            response = client.chat.completions.create(
                model=model_name,
                response_model=GeneratedSchema,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
        except Exception as e:
            print(f"Error with model {model_name}: {str(e)}")
            print(f"Retrying with fallback model: {fallback_model}")

            response = client.chat.completions.create(
                model=fallback_model,
                response_model=GeneratedSchema,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )

        structured_info = response

        if structured_info:
            try:
                structured_info_dict = structured_info.model_dump()
                rt.end(outputs=structured_info_dict)
                rt.post()
                return json.dumps(structured_info_dict, indent=2)
            except ValidationError as e:
                print(f"Validation Error: {str(e)}")
                error_messages = []
                for error in e.errors():
                    field = error["loc"][0]
                    message = error["msg"]
                    error_messages.append(f"{field}: {message}")

                rt.end(outputs={"errors": error_messages})
                rt.post()
                return json.dumps({"errors": error_messages}, indent=2)
        else:
            rt.end(outputs=None)
            rt.post()
            return None

    @traceable(run_type="llm", name="process_resume_mixtral", project_name="Data-Extractor")
    @observe()
    async def process_resume_anyscale(self, text, model_name, fallback_model):
        fields_data = self.data_schema

        prompt = f"""Please extract all the information from the given resume text and return it in the specified JSON format:

        Resume Text:
        {text}

        Structured Information (in JSON format):
        """

        GeneratedSchema = DynamicSchemaCreator.create_dynamic_schema(
            fields_data)

        rt = RunTree(
            run_type="llm",
            name="Mixtral Call RunTree",
            inputs={"messages": [
                {"role": "system", "content": "You are a world class extractor"},
                {"role": "user", "content": prompt}
            ]},
            project_name="Data-Extractor"
        )

        client = instructor.from_openai(
            OpenAI(
                base_url="https://api.endpoints.anyscale.com/v1",
                api_key=os.environ["ANYSCALE_API_KEY"],
            ),
            mode=instructor.Mode.JSON_SCHEMA,
        )

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a world class extractor"},
                    {"role": "user", "content": prompt}
                ],
                response_model=GeneratedSchema,
            )
        except Exception as e:
            print(f"Error with model {model_name}: {str(e)}")
            print(f"Retrying with fallback model: {fallback_model}")

            response = client.chat.completions.create(
                model=fallback_model,
                messages=[
                    {"role": "system", "content": "You are a world class extractor"},
                    {"role": "user", "content": prompt}
                ],
                response_model=GeneratedSchema,
            )

        structured_info = response

        if structured_info:
            try:
                structured_info_dict = structured_info.model_dump()
                rt.end(outputs=structured_info_dict)
                rt.post()
                return json.dumps(structured_info_dict, indent=2)
            except ValidationError as e:
                print(f"Validation Error: {str(e)}")
                error_messages = []
                for error in e.errors():
                    field = error["loc"][0]
                    message = error["msg"]
                    error_messages.append(f"{field}: {message}")

                rt.end(outputs={"errors": error_messages})
                rt.post()
                return json.dumps({"errors": error_messages}, indent=2)
        else:
            rt.end(outputs=None)
            rt.post()
            return None
