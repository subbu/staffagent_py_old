from pydantic import BaseModel, create_model, Field, field_validator
from typing import List, Any

class DynamicSchemaCreator:
    @staticmethod
    def create_dynamic_schema(fields_data):
        types = {
            'string': str,
            'integer': int,
            'boolean': bool,
            'array': List,
        }

        fields = {}
        validators = {}

      

        

        def create_field_validator(field_name, field_info):
            def validate_field(v):
                if not isinstance(v, field_info.get('data_type', Any)):
                    raise ValueError(f"{field_name} must be of type {field_info.get('data_type', Any)}")
                if 'fields' in field_info:
                    for item in v:
                        for sub_field_name, sub_field_info in field_info['fields'].items():
                            sub_field_value = item.get(sub_field_name)
                            if sub_field_info.get('required', False) and sub_field_value is None:
                                raise ValueError(f"{sub_field_name} is required in {field_name}")
                            if sub_field_value is not None and not isinstance(sub_field_value, sub_field_info.get('data_type', Any)):
                                raise ValueError(f"{sub_field_name} in {field_name} must be of type {sub_field_info.get('data_type', Any)}")
                return v
            return field_validator(field_name)(validate_field)

        for field_info in fields_data:
           field_name = field_info['name']
           field_type = field_info['data_type']
           default_value = field_info.get('default', ...)
           required = field_info.get('required', False)

           if field_type == 'array' and 'fields' in field_info:
               nested_fields = field_info['fields']
               field_type = List[DynamicSchemaCreator.create_dynamic_schema(nested_fields)]
           elif field_type in types:
               field_type = types[field_type]
           else:
               raise ValueError(f"Unsupported field type: {field_type}")

           if required:
             fields[field_name] = (field_type, Field(..., description=f"The {field_name} field."))
           else:
             fields[field_name] = (field_type, Field(default_value, description=f"The {field_name} field."))

           validators[field_name] = create_field_validator(field_name, field_info)


        
        DynamicSchema = create_model(
            'DynamicSchema',
            **fields,
            __field_validators__=validators,
            __base__=BaseModel,
        )

    

        return DynamicSchema