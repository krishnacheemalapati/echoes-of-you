import os
import httpx

RIBBON_API_KEY = os.environ.get("RIBBON_API_KEY")
RIBBON_BASE_URL = "https://api.ribbon.ai/v1"

headers = {
    "Authorization": f"Bearer {RIBBON_API_KEY}",
    "Content-Type": "application/json",
}

def create_interview_flow(questions):
    url = f"{RIBBON_BASE_URL}/interview-flows"
    payload = {"questions": questions}
    response = httpx.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["id"]

def create_interview(interview_flow_id):
    url = f"{RIBBON_BASE_URL}/interviews"
    payload = {"interview_flow_id": interview_flow_id}
    response = httpx.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["interview_link"], data["id"]

def get_interview_status(interview_id):
    url = f"{RIBBON_BASE_URL}/interviews/{interview_id}"
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
