import requests

headers = {
    'accept': 'application/json',
    'authorization': 'Bearer efbc484a-e854-4465-9426-b98e97bd35db',
    'content-type': 'application/json',
}

json_data = {
    'org_name': "McDonald's",
    'title': 'Survey',
    'questions': [
        "When and where was the last time you visited McDonald's?",
        "What's your favorite item on the McDonald's menu?",
        'If you could introduce one new item to the menu, what would you introduce?',
    ],
}

response = requests.post('https://app.ribbon.ai/be-api/v1/interview-flows', headers=headers, json=json_data)

print(response.status_code)
print(response.json())

code = response.json().get('interview_flow_id')
# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{  "org_name": "McDonald\'s",  "title": "Survey",  "questions": [    "When and where was the last time you visited McDonald\'s?",    "What\'s your favorite item on the McDonald\'s menu?",    "If you could introduce one new item to the menu, what would you introduce?"  ]}'
#response = requests.post('https://app.ribbon.ai/be-api/v1/interview-flows', headers=headers, data=data)

headers = {
    'accept': 'application/json',
    'authorization': 'Bearer efbc484a-e854-4465-9426-b98e97bd35db',
    'content-type': 'application/json',
}

json_data = {
    'interview_flow_id': code,
}

response = requests.post('https://app.ribbon.ai/be-api/v1/interviews', headers=headers, json=json_data)

print(response.status_code)
print(response.json())

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '\n{\n  "interview_flow_id": "<your-interview-flow-id>"\n}\n'
#response = requests.post('https://app.ribbon.ai/be-api/v1/interviews', headers=headers, data=data)