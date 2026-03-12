from voice_module import recognize_from_microphone, speak
from Pentagon import ask_Pentagon, setup_pentagon 
from prompt_config import COLOR_THEME
from datetime import datetime
import os

# 🔹 Terminal saaf
os.system('cls' if os.name == 'nt' else 'clear')

# 🔹 Welcome setup
setup_pentagon()

# 🔁 Mode Selection
mode = input("\n🎮 Enter mode (voice/text): ").strip().lower()
if mode not in ["voice", "text"]:
    mode = "text"

# 🚀 DIRECT STARTUP (Bina Wake Word Ki Bakwaas Ke)
if mode == "voice":
    print(COLOR_THEME["pentagon"] + "\n🚀 System Online! Direct Voice Mode Activated." + COLOR_THEME["reset"])
    speak("Haan bhai, system online hai. Bol kya kaam hai?", input_mode="voice")

# 🔁 Main Interaction Loop
while True:
    timestamp = datetime.now().strftime("[%H:%M:%S] ")

    # --- INPUT LENA ---
    if mode == "voice":
        query = recognize_from_microphone(duration=5) # 5 seconds tak dhyan se sunega
        if not query:
            continue
        print(COLOR_THEME["user"] + f"{timestamp}You (Voice): " + COLOR_THEME["reset"] + query)
    else:
        query = input(COLOR_THEME["user"] + f"\n{timestamp}You: " + COLOR_THEME["reset"]).strip()

    # --- MODE SWITCH & EXIT CHECK ---
    if query.lower() == "switch":
        mode = "text" if mode == "voice" else "voice"
        print(COLOR_THEME["info"] + f"{timestamp}🔁 Mode switched to {mode.upper()}." + COLOR_THEME["reset"])
        continue
        
    # Exit keywords thode badha diye hain
    if query.lower() in ["exit", "quit", "bye", "band ho ja", "stop", "chup ho ja"]:
        goodbye = "Theek hai bhai, milte hain phir."
        print(COLOR_THEME["pentagon"] + f"{timestamp}Pentagon: " + COLOR_THEME["reset"] + goodbye)
        speak(goodbye, input_mode=mode)
        break

    # --- PENTAGON AI RESPONSE ---
    try:
        response = ask_Pentagon(query) 
        print(COLOR_THEME["pentagon"] + f"{timestamp}Pentagon: " + COLOR_THEME["reset"] + response.strip())
        speak(response, input_mode=mode)
    except Exception as e:
        print(COLOR_THEME["error"] + f"{timestamp}[!] Pentagon Brain Error: {e}" + COLOR_THEME["reset"])