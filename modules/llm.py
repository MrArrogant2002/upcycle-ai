"""
llm.py - Gemini API integration for generating upcycling ideas.
Uses gemini-2.0-flash via Google AI Studio.
"""
from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
#GEMINI_MODEL = "gemini-3-flash"

SYSTEM_PROMPT = """You are an eco-friendly upcycling expert and creative DIY guide.
Given a list of detected household waste objects, suggest practical and creative ways to upcycle them.
For each idea provide a catchy title, required materials, step-by-step instructions, and the final use.
Format in Markdown with clear headers. Keep tone friendly and eco-conscious.
Use section dividers (---) between ideas."""

USER_PROMPT_TEMPLATE = """Detected objects:
{objects_list}

For each object (or combination), suggest 1-2 creative upcycling ideas with:
- Title and emoji
- Materials needed
- Step-by-step instructions (4-6 steps)
- Final use / benefit

Keep ideas practical and eco-friendly."""

NO_OBJECTS_MESSAGE = """## Nothing Detected Yet
No recognisable waste objects found. Try a well-lit photo and fill the frame with the objects."""


def get_upcycle_ideas(detected_objects: list[str]) -> str:
    if not detected_objects:
        return NO_OBJECTS_MESSAGE

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return (
            "## ⚠️ API Key Not Configured\n\n"
            "Add your Gemini API key to `.env`:\n\n"
            "```\nGEMINI_API_KEY=AIza...\n```\n\n"
            f"**Detected objects:** {', '.join(detected_objects)}"
        )

    try:
        from google import genai
        from google.genai import types as genai_types

        client = genai.Client(api_key=api_key)
        objects_list = "\n".join(f"- {obj}" for obj in detected_objects)
        user_message = USER_PROMPT_TEMPLATE.format(objects_list=objects_list)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_message,
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=2048,
            ),
        )
        return response.text

    except Exception as exc:
        exc_str = str(exc).lower()
        objs = ", ".join(detected_objects)
        if "api_key" in exc_str or "api key" in exc_str or "invalid" in exc_str or "unauthorized" in exc_str:
            return (
                "## 🔑 Invalid API Key\n\n"
                "Verify your Gemini API key at [aistudio.google.com](https://aistudio.google.com/app/apikey).\n\n"
                f"**Detected objects (saved):** {objs}"
            )
        if "quota" in exc_str or "resource_exhausted" in exc_str or "429" in exc_str:
            return (
                "## ⏱️ Rate Limit Reached\n\n"
                "Gemini API quota exceeded. Please wait and try again.\n\n"
                f"**Detected objects (saved):** {objs}"
            )
        if "connection" in exc_str or "network" in exc_str or "transport" in exc_str or "timeout" in exc_str:
            return (
                "## 🔌 Connection Error\n\n"
                "Could not reach the Gemini API. Check your internet connection.\n\n"
                f"**Detected objects (saved):** {objs}"
            )
        return (
            f"## ❌ Unexpected Error\n\n"
            f"`{type(exc).__name__}: {exc}`\n\n"
            f"**Detected objects (saved):** {objs}"
        )
