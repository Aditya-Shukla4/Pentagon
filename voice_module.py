# voice_module.py
# ─────────────────────────────────────────────────────────────
# Handles all voice I/O:
#   - Microphone input  → Whisper STT
#   - Text output       → Edge TTS + pygame playback
# ─────────────────────────────────────────────────────────────

import warnings
warnings.filterwarnings("ignore")

import os
import asyncio
import scipy.io.wavfile as wav

import sounddevice as sd
import whisper
import edge_tts
import pygame

from prompt_config import (
    TTS_VOICE,
    TTS_RATE,
    WHISPER_MODEL,
    MIC_DURATION,
    MIC_SAMPLERATE,
)

# ─────────────────────────────────────────────────────────────
# Whisper model — loaded ONCE at module level, reused every call
# ─────────────────────────────────────────────────────────────

_whisper_model = None

def _get_whisper_model():
    """Load Whisper model once and cache it for the session."""
    global _whisper_model
    if _whisper_model is None:
        print("[~] Loading Whisper model (one-time setup)...")
        _whisper_model = whisper.load_model(WHISPER_MODEL)
        print("[✓] Whisper model loaded.")
    return _whisper_model


# ─────────────────────────────────────────────────────────────
# 🎙️ Voice Input (STT via Whisper)
# ─────────────────────────────────────────────────────────────

def recognize_from_microphone(duration=MIC_DURATION, fs=MIC_SAMPLERATE):
    """
    Record audio from the default microphone and transcribe it using Whisper.

    Args:
        duration (int): Recording length in seconds.
        fs (int): Sample rate in Hz.

    Returns:
        str: Transcribed text, or empty string on failure.
    """
    try:
        print(f"\n🎙️  Listening for {duration} seconds... (stay quiet until done)")

        # Record from default system microphone
        recording = sd.rec(
            int(duration * fs),
            samplerate=fs,
            channels=1,
            dtype="int16"
        )
        sd.wait()  # Block until recording is complete

        # Save to temp wav file for Whisper
        wav.write("audio.wav", fs, recording)

        # Transcribe using cached model
        model = _get_whisper_model()
        result = model.transcribe("audio.wav", language="en")
        text = result["text"].strip()

        if text:
            return text
        else:
            print("🤔 Didn't catch that. Please try again.")
            return ""

    except Exception as e:
        print(f"[!] Mic Error: {e}")
        return ""


# ─────────────────────────────────────────────────────────────
# 🔊 Voice Output (TTS via Edge TTS + pygame)
# ─────────────────────────────────────────────────────────────

async def _speak_async(text: str):
    """Async core: generate TTS audio and play it via pygame."""
    output_file = "output.mp3"

    # Remove old file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)

    # Generate speech
    communicate = edge_tts.Communicate(text, voice=TTS_VOICE, rate=TTS_RATE)
    await communicate.save(output_file)

    # Play audio
    pygame.mixer.init()
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()

    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()


def speak(text: str, input_mode: str = "voice"):
    """
    Speak the given text aloud — only in voice mode.

    Args:
        text (str): Text to speak.
        input_mode (str): "voice" to speak, "text" to stay silent.
    """
    if input_mode != "voice":
        return  # Silent in text mode

    if not text or not text.strip():
        return

    try:
        # Use a fresh event loop to avoid conflicts with any existing loops
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_speak_async(text))
        finally:
            loop.close()
    except Exception as e:
        print(f"[!] TTS Error: {e}")