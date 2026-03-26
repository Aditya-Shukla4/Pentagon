# Pentagon.py
# ─────────────────────────────────────────────────────────────
# Core AI engine:
#   - Ollama health check on startup
#   - LLaMA3 via Ollama REST API
#   - SymPy math validation layer
# ─────────────────────────────────────────────────────────────

import sys
import requests
from colorama import Fore, Style
from sympy import (
    symbols, diff, integrate, limit,
    solve, simplify, exp, re, im, sin, I
)
from sympy.parsing.sympy_parser import parse_expr

from prompt_config import (
    SYSTEM_PROMPT,
    COLOR_THEME,
    OLLAMA_URL,
    OLLAMA_MODEL,
    OLLAMA_PARAMS,
)

# ─────────────────────────────────────────────────────────────
# Global SymPy symbols
# ─────────────────────────────────────────────────────────────

x, y, z, t = symbols("x y z t")


# ─────────────────────────────────────────────────────────────
# Ollama health check
# ─────────────────────────────────────────────────────────────

def check_ollama():
    """
    Verify Ollama is running before starting Pentagon.
    Exits with a helpful message if not reachable.
    """
    try:
        response = requests.get("http://localhost:11434", timeout=3)
        # Ollama returns 200 when healthy
    except requests.exceptions.ConnectionError:
        print(
            COLOR_THEME["error"]
            + "\n[!] Ollama is not running."
            + COLOR_THEME["reset"]
            + "\n    Start it with:  ollama serve"
            + "\n    Then run:       ollama pull llama3\n"
        )
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(
            COLOR_THEME["error"]
            + "\n[!] Ollama is not responding (timeout)."
            + COLOR_THEME["reset"]
            + "\n    Try restarting: ollama serve\n"
        )
        sys.exit(1)


# ─────────────────────────────────────────────────────────────
# SymPy helpers
# ─────────────────────────────────────────────────────────────

def _extract_expr(prompt: str):
    """Extract a SymPy expression from the user's prompt."""
    try:
        for keyword in ["differentiate", "derivative", "integrate", "solve"]:
            if keyword in prompt.lower():
                expr_text = prompt.lower().split(keyword)[1].strip()
                return parse_expr(expr_text, evaluate=False)
    except Exception:
        pass
    return x  # fallback


def _extract_limit(_prompt: str):
    """Extract limit parameters — returns (expr, var, point)."""
    # Basic implementation: defaults to lim(sin(x)/x, x→0)
    # Extend this to parse more complex limit expressions if needed
    return sin(x) / x, x, 0


def validate_math_answer(prompt: str, _answer: str) -> str:
    """
    Run SymPy validation on math-related queries.
    Returns a formatted result string, or an info message if not applicable.
    """
    prompt_lower = prompt.lower()

    try:
        if "differentiate" in prompt_lower or "derivative" in prompt_lower:
            expr = _extract_expr(prompt)
            return f"✅ Derivative: {diff(expr)}"

        elif "integrate" in prompt_lower:
            expr = _extract_expr(prompt)
            return f"✅ Integral: {integrate(expr)} + C"

        elif "limit" in prompt_lower:
            expr, var, point = _extract_limit(prompt)
            return f"✅ Limit: {limit(expr, var, point)}"

        elif "solve" in prompt_lower:
            expr = _extract_expr(prompt)
            return f"✅ Solution: {solve(expr, x)}"

        elif "analytic" in prompt_lower or "real part" in prompt_lower:
            expr = exp(x + I * y)
            u = simplify(re(expr))
            v = simplify(im(expr))
            du_dx = diff(u, x)
            dv_dy = diff(v, y)
            du_dy = diff(u, y)
            dv_dx = diff(v, x)

            is_analytic = (
                simplify(du_dx - dv_dy) == 0
                and simplify(du_dy + dv_dx) == 0
            )
            status = "✅ Function is analytic." if is_analytic else "❌ Function is not analytic."
            return f"{status}\n✅ Real part: {u}\n✅ Imaginary part: {v}"

        else:
            return "ℹ️ SymPy validation not applicable."

    except Exception as e:
        return f"❌ [SymPy Error] {str(e)}"


# ─────────────────────────────────────────────────────────────
# Main AI engine
# ─────────────────────────────────────────────────────────────

def ask_Pentagon(prompt: str) -> str:
    """
    Send a prompt to LLaMA3 via Ollama and return the response.
    Appends SymPy validation for math queries.

    Args:
        prompt (str): User's input text.

    Returns:
        str: Pentagon's response.
    """
    # Input validation
    if not isinstance(prompt, str) or not prompt.strip():
        return "[!] Error: Empty or invalid input."

    prompt_clean = prompt.strip().lower()

    # Quick reply for greetings — no need to hit the model
    if prompt_clean in ["hi", "hello", "hey", "heyy", "hii"]:
        return (
            "Aree bhai! 😄\n"
            "Welcome back — kya scene hai aaj? Study, coding, ya kuch aur? 🔥"
        )

    # Build full prompt: system instructions + user message
    full_prompt = SYSTEM_PROMPT + "\n\nUser: " + prompt.strip()

    # Call Ollama
    try:
        res = requests.post(
            OLLAMA_URL,
            json={
                "model":          OLLAMA_MODEL,
                "prompt":         full_prompt,
                "stream":         False,
                **OLLAMA_PARAMS,
            },
            timeout=60,  # Generous timeout for longer answers
        )
        res.raise_for_status()
        data = res.json()
        response_text = data.get("response", "").strip()

        if not response_text:
            return "[!] Pentagon got an empty response. Try again."

    except requests.exceptions.Timeout:
        return (
            "[!] Ollama timed out. The model might still be loading.\n"
            "    Wait a few seconds and try again."
        )
    except requests.exceptions.ConnectionError:
        return (
            "[!] Lost connection to Ollama.\n"
            "    Make sure it's running:  ollama serve"
        )
    except requests.exceptions.HTTPError as e:
        return f"[!] Ollama returned an error: {e}"
    except Exception as e:
        return f"[!] Unexpected error: {e}"

    # Append SymPy validation for math questions
    validation_result = validate_math_answer(prompt, response_text)
    if not validation_result.startswith("ℹ️"):
        response_text += "\n\n🧠 SymPy Validation:\n" + validation_result

    return response_text


# ─────────────────────────────────────────────────────────────
# Boot sequence
# ─────────────────────────────────────────────────────────────

def setup_pentagon():
    """Run startup checks and print the welcome banner."""
    print(COLOR_THEME["info"] + "Starting Pentagon..." + COLOR_THEME["reset"])

    # Check Ollama before anything else
    check_ollama()

    print(
        COLOR_THEME["pentagon"]
        + "\nPentagon: 🔥 Pentagon is now online. Bol kya scene hai — study, chill, ya coding?"
        + COLOR_THEME["reset"]
    )
    print()