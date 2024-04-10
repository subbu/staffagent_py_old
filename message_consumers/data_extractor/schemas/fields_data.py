fields_data = [
    {
        "name": "name",
        "type": "string",
        "default": "Not specified",
        "required": True
    },
    {
        "name": "email",
        "type": "string",
        "default": "Not specified",
        "required": True
    },
    {
        "name": "phone",
        "type": "string",
        "default": "Not specified",
        "required": True
    },
    {
        "name": "skills",
        "type": "array",
        "default": [],
        "required": True
    },
   
    {
        "name": "education",
        "type": "array",
        "default": [],
        "required": True
    },
    
    {
        "name": "languages",
        "type": "array",
        "default": [],
        "required": False
    },
    {
        "name": "certifications",
        "type": "array",
        "default": [],
        "required": False
    },
    {
        "name": "address",
        "type": "string",
        "default": "Not specified",
        "required": False
    },
     {
        "name": "experience",
        "type": "array",
        "default": [],
        "required": False,
        "fields": [
            {"name": "company", "type": "string", "required": True},
            {"name": "position", "type": "string", "required": True},
            {"name": "duration", "type": "string", "required": True},
            {"name": "description", "type": "string", "required": False}
        ]
    },
   
    {
        "name": "projects",
        "type": "array",
        "default": [],
        "required": False,
        "fields": [
            {"name": "name", "type": "string", "required": True},
            {"name": "description", "type": "string", "required": True},
            {"name": "technologies", "type": "array", "default": [], "required": False}
        ]
    }
]