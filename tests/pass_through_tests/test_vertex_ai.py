"""
Test Vertex AI Pass Through

1. use Credentials client side, Assert SpendLog was created
"""

import vertexai
from vertexai.preview.generative_models import GenerativeModel
import tempfile
import json
import os
import pytest


# Path to your service account JSON file
SERVICE_ACCOUNT_FILE = "path/to/your/service-account.json"


def load_vertex_ai_credentials():
    # Define the path to the vertex_key.json file
    print("loading vertex ai credentials")
    filepath = os.path.dirname(os.path.abspath(__file__))
    vertex_key_path = filepath + "/vertex_key.json"

    # Read the existing content of the file or create an empty dictionary
    try:
        with open(vertex_key_path, "r") as file:
            # Read the file content
            print("Read vertexai file path")
            content = file.read()

            # If the file is empty or not valid JSON, create an empty dictionary
            if not content or not content.strip():
                service_account_key_data = {}
            else:
                # Attempt to load the existing JSON content
                file.seek(0)
                service_account_key_data = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, create an empty dictionary
        service_account_key_data = {}

    # Update the service_account_key_data with environment variables
    private_key_id = os.environ.get("VERTEX_AI_PRIVATE_KEY_ID", "")
    private_key = os.environ.get("VERTEX_AI_PRIVATE_KEY", "")
    private_key = private_key.replace("\\n", "\n")
    service_account_key_data["private_key_id"] = private_key_id
    service_account_key_data["private_key"] = private_key

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        # Write the updated content to the temporary files
        json.dump(service_account_key_data, temp_file, indent=2)

    # Export the temporary file as GOOGLE_APPLICATION_CREDENTIALS
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(temp_file.name)


async def call_spend_logs_endpoint():
    """
    Call this
    curl -X GET "http://0.0.0.0:4000/spend/logs?start_date={}" -H "Authorization: Bearer sk-1234"
    """
    import datetime
    import requests

    todays_date = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"http://0.0.0.0:4000/spend/logs?start_date={todays_date}"
    headers = {"Authorization": f"Bearer sk-1234"}
    response = requests.get(url, headers=headers)
    print("response from call_spend_logs_endpoint", response)

    return response


LITE_LLM_ENDPOINT = "http://localhost:4000"


@pytest.mark.asyncio()
async def test_basic_vertex_ai_pass_through_with_spendlog():
    load_vertex_ai_credentials()
    vertexai.init(
        project="adroit-crow-413218",
        location="us-central1",
        api_endpoint=f"{LITE_LLM_ENDPOINT}/vertex-ai",
        api_transport="rest",
    )

    model = GenerativeModel(model_name="gemini-1.0-pro")
    response = model.generate_content("hi")

    print("response", response)

    _spend_logs_response = await call_spend_logs_endpoint()
    print("spend logs response", _spend_logs_response)

    pass
