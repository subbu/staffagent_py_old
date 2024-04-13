from models.dynamic_schema import DynamicSchemaCreator
# from schemas.fields_data import fields_data
from openai import OpenAI
from instructor import patch
import instructor
from pydantic import ValidationError
import json

class ResumeProcessor:
    def __init__(self, openai_api_key,data_schema):
        self.openai_client = instructor.patch(OpenAI(api_key=openai_api_key))
        self.data_schema = data_schema

    def process_resume(self, text):

        fields_data  = self.data_schema

     
        
        prompt = f"""Please extract all the  information from the given resume text and return it in the specified JSON format:

        Resume Text:
        {text}

        Structured Information (in JSON format):
        """


        GeneratedSchema = DynamicSchemaCreator.create_dynamic_schema(fields_data)


       

        

        try:
            response = self.openai_client.chat.completions.create( #type:ignore
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system", "content": "You are an AI assistant that extracts structured information from resumes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                n=1,
                stop=None,
                temperature=0.7,
                response_model=GeneratedSchema
            )

            structured_info = response
            
            if structured_info:
                try:
                    structured_info_dict = structured_info.dict()
                    return json.dumps(structured_info_dict, indent=2)
                except ValidationError as e:
                    print(f"Validation Error: {str(e)}")
                    error_messages = []
                    for error in e.errors():
                        field = error["loc"][0]
                        message = error["msg"]
                        error_messages.append(f"{field}: {message}")
                    return json.dumps({"errors": error_messages}, indent=2)
            else:
                return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None