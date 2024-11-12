import base64
import boto3
import json
import os
from botocore.exceptions import ClientError

def get_image_description(client, uploaded_file, prompt, model_choice):
    # Encode the uploaded image in base64
    encoded_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

    # Create the GPT-4o or GPT-4o-mini API request
    response = client.chat.completions.create(
        model=model_choice,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded_image}"}
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    # Extract and return the description
    return response.choices[0].message.content

# Function to get the OpenAI API key from AWS Secrets Manager
def get_secret():
    secret_name = "openAI_key_warsztaty_PW_2024"
    region_name = "us-east-1"

    try:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        return json.loads(get_secret_value_response['SecretString'])
    except Exception as e:
        print(f"Error fetching secret: {e}")
        # Fallback to local .env or environment variables
        return {
            "openAI_key_warsztaty_PW_2024": os.environ.get("OPENAI_API_KEY"),
            # Add other secrets as needed
        }
