from django.conf import settings
from openai import OpenAI


def get_nvidia_client():
    if not settings.NVIDIA_API_KEY:
        raise RuntimeError("Missing NVIDIA_API_KEY in .env")

    return OpenAI(
        base_url=settings.NVIDIA_BASE_URL,
        api_key=settings.NVIDIA_API_KEY,
    )


def ask_llm(prompt):
    client = get_nvidia_client()

    try:
        response = client.responses.create(
            model=settings.NVIDIA_MODEL,
            input=prompt,
            max_output_tokens=4096,
            top_p=1,
            temperature=0.4,
            stream=False,
        )
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text
    except Exception:
        pass

    # Fallback for providers that expose OpenAI-compatible chat completions only.
    completion = client.chat.completions.create(
        model=settings.NVIDIA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        top_p=1,
        temperature=0.4,
        stream=False,
    )
    return completion.choices[0].message.content
