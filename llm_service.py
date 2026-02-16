# ==============================
# Main Imports
# ==============================

import asyncio
from pathlib import Path

# ==============================
# OpenAi Imports
# ==============================

from openai import OpenAI, RateLimitError, APIError, APIConnectionError

# ==============================
# Configuration & Constants
# ==============================

SYSTEM_PROMPT_CACHE = ""
LEAGUE_DATA_CACHE = ""

# ==============================
# Prompt Loading & LLM
# ==============================

def _read_text(path: str, fallback: str = "") -> str:
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return fallback
    
def load_system_prompt() -> str:
    global SYSTEM_PROMPT_CACHE
    if not SYSTEM_PROMPT_CACHE:
        SYSTEM_PROMPT_CACHE = _read_text("prompts/system_prompt.txt", fallback="You are The Bribe Scribe.")
    return SYSTEM_PROMPT_CACHE


def load_league_data() -> str:
    global LEAGUE_DATA_CACHE
    if not LEAGUE_DATA_CACHE:
        LEAGUE_DATA_CACHE = _read_text("league_data.txt", fallback="")
    return LEAGUE_DATA_CACHE

def generate_text(client: OpenAI, user_prompt: str) -> str:

    try:
        system_prompt = load_system_prompt()
        league_data = load_league_data()

        full_prompt = system_prompt.strip()
        if league_data:
            full_prompt += "\n\nLEAGUE DATA (authoritative, do not contradict):\n" + league_data.strip()
        full_prompt += "\n\nREQUEST:\n" + user_prompt.strip()

        resp = client.responses.create(
            model="gpt-5-mini",
            input=full_prompt,
        )

        text = resp.output_text.strip()
        return text.replace("@everyone", "everyone").replace("@here", "here")

    except RateLimitError:
        return ("The Bribe Scribe is temporarily out of ink and coin. "
                "Try again later once the bookmakers have topped up the purse.")
    except (APIConnectionError, APIError):
        return ("The Bribe Scribe cannot reach the wire right now. "
                "Try again in a moment.")
    except Exception:
        return ("The Bribe Scribe had an… incident. Try again shortly.")

async def generate_text_async(client: OpenAI, user_prompt: str) -> str:
    return await asyncio.to_thread(generate_text, client, user_prompt)