# run.py
# ─────────────────────────────────────────────────────────────
# Pentagon entry point:
#   - Mode selection (voice / text)
#   - Main interaction loop
#   - Mode switching mid-session
# ─────────────────────────────────────────────────────────────

import os
from datetime import datetime

from Pentagon import ask_Pentagon, setup_pentagon
from voice_module import recognize_from_microphone, speak
from prompt_config import COLOR_THEME

# ─────────────────────────────────────────────────────────────
# Startup
# ─────────────────────────────────────────────────────────────

# Clear terminal
os.system("cls" if os.name == "nt" else "clear")

# Run health checks + print banner
# (also calls check_ollama() internally — will exit if Ollama is down)
setup_pentagon()

# ─────────────────────────────────────────────────────────────
# Mode selection
# ─────────────────────────────────────────────────────────────

while True:
    mode = input(
        COLOR_THEME["info"]
        + "🎮 Enter mode (voice / text): "
        + COLOR_THEME["reset"]
    ).strip().lower()

    if mode in ["voice", "text"]:
        break
    print(COLOR_THEME["error"] + "   Invalid mode. Type 'voice' or 'text'." + COLOR_THEME["reset"])

if mode == "voice":
    print(
        COLOR_THEME["pentagon"]
        + "\n🚀 Voice Mode Active — Bol bhai, sun raha hoon!\n"
        + COLOR_THEME["reset"]
    )
    speak("Haan bhai, system online hai. Bol kya kaam hai?", input_mode="voice")
else:
    print(
        COLOR_THEME["pentagon"]
        + "\n💬 Text Mode Active — Type your question below.\n"
        + COLOR_THEME["reset"]
    )

# ─────────────────────────────────────────────────────────────
# Exit keywords
# ─────────────────────────────────────────────────────────────

EXIT_COMMANDS = {
    "exit", "quit", "bye", "band ho ja",
    "stop", "chup ho ja", "bas", "done"
}

# ─────────────────────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────────────────────

while True:
    timestamp = COLOR_THEME["dim"] + datetime.now().strftime("[%H:%M:%S] ") + COLOR_THEME["reset"]

    # ── Get input ──────────────────────────────────────────────
    if mode == "voice":
        query = recognize_from_microphone()
        if not query:
            continue  # Nothing heard — keep listening
        print(
            timestamp
            + COLOR_THEME["user"] + "You (Voice): " + COLOR_THEME["reset"]
            + query
        )
    else:
        try:
            query = input(
                "\n" + timestamp
                + COLOR_THEME["user"] + "You: " + COLOR_THEME["reset"]
            ).strip()
        except (EOFError, KeyboardInterrupt):
            # Ctrl+C or Ctrl+D — clean exit
            print()
            query = "exit"

    if not query:
        continue

    # ── Mode switch ────────────────────────────────────────────
    if query.lower() == "switch":
        mode = "text" if mode == "voice" else "voice"
        msg = f"🔁 Switched to {mode.upper()} mode."
        print(timestamp + COLOR_THEME["info"] + msg + COLOR_THEME["reset"])
        if mode == "voice":
            speak("Voice mode on. Bol bhai.", input_mode="voice")
        continue

    # ── Exit ───────────────────────────────────────────────────
    if query.lower() in EXIT_COMMANDS:
        goodbye = "Theek hai bhai, milte hain phir. Take care! 👋"
        print(
            timestamp
            + COLOR_THEME["pentagon"] + "Pentagon: " + COLOR_THEME["reset"]
            + goodbye
        )
        speak(goodbye, input_mode=mode)
        break

    # ── Get Pentagon's response ────────────────────────────────
    try:
        response = ask_Pentagon(query)
        print(
            "\n" + timestamp
            + COLOR_THEME["pentagon"] + "Pentagon: " + COLOR_THEME["reset"]
            + response.strip()
        )
        speak(response, input_mode=mode)

    except Exception as e:
        error_msg = f"[!] Pentagon Brain Error: {e}"
        print(timestamp + COLOR_THEME["error"] + error_msg + COLOR_THEME["reset"])