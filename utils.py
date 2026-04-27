import base64
import os
from dotenv import load_dotenv

load_dotenv()

def get_image_description(client, uploaded_file, prompt, model_choice):
    encoded_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    mime_type = uploaded_file.type or "image/png"

    response = client.chat.completions.create(
        model=model_choice,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"}
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content

def resolve_api_key():
    return os.environ.get("OPENAI_API_KEY", "")
