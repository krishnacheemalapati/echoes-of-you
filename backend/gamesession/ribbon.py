import os
import requests


import logging
RIBBON_API_KEY = os.environ.get("RIBBON_API_KEY")
RIBBON_BASE_URL = "https://app.ribbon.ai/be-api/v1"

headers = {
    'accept': 'application/json',
    'authorization': f'Bearer {RIBBON_API_KEY}',
    'content-type': 'application/json',
}

def create_interview_flow(questions, org_name="Echoes of You", title="Interrogation Interview"):
    print("ribbon.xyz")  # Place this in ribbon.py just before logging the API key
    url = f"{RIBBON_BASE_URL}/interview-flows"
    webhook_url = get_ribbon_webhook_url()
    payload = {
        "org_name": org_name,
        "title": title,
        "questions": questions,
        "webhook_url": webhook_url
    }
    logging.info(f"[DEBUG] Ribbon payload: {payload}")
    try:
        try:
            response = requests.post(url, headers=headers, json=payload)
        except Exception as req_exc:
            print(f"[DEBUG] Exception during requests.post: {req_exc}")
            logging.error(f"Ribbon API requests.post error: {req_exc}")
            raise
        print(f"[DEBUG] Ribbon API status: {response.status_code}")
        print(f"[DEBUG] Ribbon API headers: {response.headers}")
        print(f"[DEBUG] Ribbon API raw response: {response.text}")
        response.raise_for_status()
        try:
            data = response.json()
        except Exception:
            print(f"[DEBUG] Ribbon API returned non-JSON response: {response.text}")
            logging.error(f"Ribbon API returned non-JSON response: {response.text}")
            raise ValueError(f"Ribbon API did not return JSON. Response: {response.text}")
        if not isinstance(data, dict) or "interview_flow_id" not in data:
            print(f"[DEBUG] Ribbon API unexpected response: {data}")
            logging.error(f"Ribbon API unexpected response: {data}")
            raise ValueError(f"Ribbon API did not return interview_flow_id. Response: {data}")
        return data["interview_flow_id"]
    except Exception as e:
        print(f"[DEBUG] Ribbon API error: {e}")
        logging.error(f"Ribbon API error in create_interview_flow: {e}\nPayload: {payload}\nResponse: {getattr(e, 'response', None)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"[DEBUG] Ribbon API response text: {e.response.text}")
            logging.error(f"Ribbon API response text: {e.response.text}")
        raise

def get_ribbon_webhook_url():
    # Try to get from env, else default to localhost for dev
    return os.environ.get("RIBBON_WEBHOOK_URL", "https://fd51ae000780.ngrok-free.app/api/game/ribbon-webhook")

def create_interview(interview_flow_id):
    url = f"{RIBBON_BASE_URL}/interviews"
    payload = {"interview_flow_id": interview_flow_id}
    logging.info(f"[DEBUG] Ribbon create_interview payload: {payload}")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or "interview_link" not in data or "interview_id" not in data:
            logging.error(f"Ribbon API unexpected response: {data}")
            raise ValueError(f"Ribbon API did not return interview_link or interview_id. Response: {data}")
        return data["interview_link"], data["interview_id"]
    except Exception as e:
        logging.error(f"Ribbon API error in create_interview: {e}\nPayload: {payload}\nResponse: {getattr(e, 'response', None)}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Ribbon API response text: {e.response.text}")
        raise

def get_interview_status(interview_id):
    url = f"{RIBBON_BASE_URL}/interviews/{interview_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Ribbon API error in get_interview_status: {e}\nResponse: {getattr(e, 'response', None)}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Ribbon API response text: {e.response.text}")
        raise
