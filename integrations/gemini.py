# integrations/gemini.py
from google import genai
from google.genai import types
from PIL import Image
import io
import config

# ── Initialize client
client = genai.Client(api_key=config.GEMINI_API_KEY)

# ── Model
MODEL = "gemini-2.0-flash"

# ──────────────────────────────────────────
# IMAGE ANALYSIS
# ──────────────────────────────────────────
def analyze_image(image_path: str, prompt: str) -> str:
    """
    Send image + prompt to Gemini vision.
    Returns raw text response.
    """
    try:
        image = Image.open(image_path)

        # convert to bytes
        buf = io.BytesIO()
        image.save(buf, format="JPEG")
        buf.seek(0)

        response = client.models.generate_content(
            model    = MODEL,
            contents = [
                types.Part.from_bytes(
                    data      = buf.read(),
                    mime_type = "image/jpeg"
                ),
                prompt
            ]
        )
        return response.text

    except Exception as e:
        print(f"❌ Gemini vision error: {e}")
        raise e

# ──────────────────────────────────────────
# TEXT GENERATION
# ──────────────────────────────────────────
def generate_text(prompt: str, system_prompt: str = None) -> str:
    """
    Send text prompt to Gemini.
    Returns raw text response.
    """
    try:
        full_prompt = (
            f"{system_prompt}\n\n{prompt}"
            if system_prompt
            else prompt
        )
        response = client.models.generate_content(
            model    = MODEL,
            contents = full_prompt
        )
        return response.text

    except Exception as e:
        print(f"❌ Gemini text error: {e}")
        raise e

# ──────────────────────────────────────────
# CHAT / CONVERSATION
# ──────────────────────────────────────────
def chat_with_history(
    history: list,
    new_message: str,
    system_prompt: str = None
) -> str:
    """
    Continue a conversation with full history.
    history format:
    [{"role": "user/model", "parts": ["message"]}]
    """
    try:
        # inject system prompt as first exchange
        if system_prompt and len(history) == 0:
            history = [
                {
                    "role":  "user",
                    "parts": [system_prompt]
                },
                {
                    "role":  "model",
                    "parts": ["Understood. I am ready to assist."]
                }
            ]

        # convert history to genai format
        formatted = []
        for entry in history:
            parts = entry.get("parts", [])
            formatted.append(
                types.Content(
                    role  = entry["role"],
                    parts = [
                        types.Part(text=p)
                        for p in parts
                    ]
                )
            )

        # add new message
        formatted.append(
            types.Content(
                role  = "user",
                parts = [types.Part(text=new_message)]
            )
        )

        response = client.models.generate_content(
            model    = MODEL,
            contents = formatted
        )
        return response.text

    except Exception as e:
        print(f"❌ Gemini chat error: {e}")
        raise e

# ──────────────────────────────────────────
# JSON RESPONSE
# ──────────────────────────────────────────
def generate_json(prompt: str) -> str:
    """
    Ask Gemini to return pure JSON.
    Strips markdown code fences automatically.
    """
    try:
        json_prompt = f"""
{prompt}

IMPORTANT: Respond with ONLY valid JSON.
No explanation, no markdown, no code fences.
Just the raw JSON object.
        """
        response = client.models.generate_content(
            model    = MODEL,
            contents = json_prompt
        )
        raw = response.text.strip()

        # strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        return raw

    except Exception as e:
        print(f"❌ Gemini JSON error: {e}")
        raise e

# ──────────────────────────────────────────
# HEALTH CHECK
# ──────────────────────────────────────────
def test_connection() -> bool:
    """Test if Gemini API is working."""
    try:
        response = generate_text("Say 'OK' and nothing else.")
        print(f"✅ Gemini connected: {response.strip()}")
        return True
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
        return False