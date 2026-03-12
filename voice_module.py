import warnings
warnings.filterwarnings("ignore")

import sounddevice as sd
import whisper
import asyncio
import edge_tts
import scipy.io.wavfile as wav
import pygame
import os

# ----------------------------------
# 🎙️ Voice Input (Kaan)
# ----------------------------------
# ----------------------------------
# 🎙️ Voice Input (Kaan)
# ----------------------------------
# ----------------------------------
# 🎙️ Voice Input (Kaan)
# ----------------------------------
def recognize_from_microphone(duration=5, fs=16000):
    try:
        print("\n🎙️ Speak now... (Listening for 5 seconds, WAIT KARNA!)")
        
        # Humne device=9 hata diya. Ab system apna default kaan use karega!
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait() # 🛑 YAHAN PYTHON 5 SECOND WAIT KAREGA, TERMINAL BAND MAT KARNA!
        wav.write("audio.wav", fs, recording)

        model = whisper.load_model("base")
        result = model.transcribe("audio.wav", language="en")
        text = result["text"].strip()

        if text:
            return text
        else:
            print("🤔 Didn't catch that. Try again.")
            return ""
    except Exception as e:
        print(f"[!] Mic Error: {e}")
        return ""
    
# ----------------------------------
# 🔊 Speak Output (Muh)
# ----------------------------------
def speak(text, input_mode="voice"):
    if input_mode != "voice":
        return  # Text mode mein shaant rahega

    try:
        async def _speak():
            if os.path.exists("output.mp3"):
                os.remove("output.mp3")

            communicate = edge_tts.Communicate(
                text,
                voice="hi-IN-MadhurNeural",
                rate="+10%" # Speed thodi normal rakhi hai
            )
            await communicate.save("output.mp3")

            pygame.mixer.init()
            pygame.mixer.music.load("output.mp3")
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()

        asyncio.run(_speak())
    except Exception as e:
        print(f"[!] TTS Error: {e}")