# Streamlit Image Processing Workshop

Upload an image, edit a prompt, and get a basic description from OpenAI vision-capable models.

Current app features:
- image upload (`jpg`, `jpeg`, `png`, `webp`)
- prompt editing with default prompt
- model selection (`gpt-4.1-mini`, `gpt-4.1-nano`)
- optional custom model override

## Local deployment

### macOS / Linux

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure API key (recommended: `.env`):

```bash
echo 'OPENAI_API_KEY="your_api_key_here"' > .env
```

Alternative for current shell only:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

4. Start the app:

```bash
streamlit run app.py
```

### Windows (PowerShell)

1. Create and activate virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Configure API key in `.env`:

```powershell
Set-Content -Path .env -Value 'OPENAI_API_KEY="your_api_key_here"'
```

Alternative for current shell only:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

4. Start the app:

```powershell
streamlit run app.py
```

Open the local URL shown by Streamlit (usually [http://localhost:8501](http://localhost:8501)).

## AWS deployment

For workshops with existing SageMaker Studio access, use SageMaker Studio first.  
For a more production-like public deployment, use AWS App Runner.

### SageMaker Studio (workshop flow)

Student steps:

```bash
git clone <YOUR_REPO_URL>
cd streamlit_image_processing
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your_api_key_here"
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Then open the app through Studio port forwarding/proxy.

Teacher checklist:
- verify student profiles can run terminal + pip install
- share one stable repo URL and branch/tag
- configure OpenAI usage limits and AWS budget alerts
- keep one backup environment running for demos

### App Runner (recommended for web deployments)

1. Containerize app (`Dockerfile`)
2. Push image to ECR
3. Deploy App Runner service from ECR image
4. Set secrets/env vars in AWS (do not hardcode keys)

## Security guidance

- Local `.env` is fine for local testing.
- For AWS/web deployments, prefer server-side secret management (AWS Secrets Manager or service env vars).
- Do not commit `.env` or API keys.
- Add authentication/rate limiting before public exposure.

### Disable manual API key input for web deployments

The app supports hiding the manual key field:

- set `DISABLE_MANUAL_API_KEY_INPUT=true` in Streamlit secrets
- provide `OPENAI_API_KEY` server-side (env var or Streamlit secrets)

This keeps keys out of the UI for deployed apps.

### App-level rate controls

The app supports per-session limits (helpful for workshop cost control):

- `MAX_REQUESTS_PER_MINUTE` (default: `5`)
- `MAX_REQUESTS_PER_DAY` (default: `100`)

Configure these using exactly one method:
- environment variables (`export ...`)
- Streamlit secrets file (`.streamlit/secrets.toml`)

Do not duplicate the same setting in both places unless you intentionally want secrets to override env values.

Option A: environment variables (good for terminal sessions):

```bash
export MAX_REQUESTS_PER_MINUTE=5
export MAX_REQUESTS_PER_DAY=100
```

Option B: `.streamlit/secrets.toml` (good for deployed Streamlit apps):

```toml
DISABLE_MANUAL_API_KEY_INPUT = true
OPENAI_API_KEY = "your_server_side_key"
MAX_REQUESTS_PER_MINUTE = 5
MAX_REQUESTS_PER_DAY = 100
```

## Troubleshooting

- `ModuleNotFoundError`: activate `.venv` and reinstall requirements.
- OpenAI `404 model_not_found`: select one of the supported models in the dropdown.
- OpenAI `401 invalid_api_key`: set/re-set `OPENAI_API_KEY`.
- Streamlit not reachable in SageMaker: check port forwarding and use `--server.address 0.0.0.0`.