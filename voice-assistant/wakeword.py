import pvporcupine
import pyaudio
import struct
import sys
import os
import io
import wave
import numpy as np
from config_manager import get_api_key, get_wakeword_config

# Load wake word configuration
wakeword_config = get_wakeword_config()
ACCESS_KEY = get_api_key('PORCUPINE_ACCESS_KEY')
MODEL_PATH = wakeword_config['model_path']
SENSITIVITY = wakeword_config.get('sensitivity', 0.5)

def wait_for_wake_word(stop_event=None):
    """
    Wait for wake word detection.
    
    Args:
        stop_event: Threading Event to signal stop (optional)
    
    Returns:
        True if wake word detected, False if stopped by event
    """
    print("Menunggu kata pemicu 'Hey Dita'...")

    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[MODEL_PATH],
        sensitivities=[SENSITIVITY]
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    try:
        while True:
            # Check if we should stop (user logged out)
            if stop_event and not stop_event.is_set():
                print("Wake word detection stopped (session ended)")
                return False
            
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm_unpacked)
            if result >= 0:
                return True

    except KeyboardInterrupt:
        print("Dihentikan oleh user.")
        return False
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()


def check_wake_word_from_audio(audio_bytes):
    """
    Check if wake word exists in audio bytes (WAV format)
    Returns True if wake word detected, False otherwise
    """
    try:
        # Parse WAV file
        audio_io = io.BytesIO(audio_bytes)
        with wave.open(audio_io, 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            audio_data = wav_file.readframes(n_frames)
        
        # Convert to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Initialize Porcupine
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[MODEL_PATH],
            sensitivities=[SENSITIVITY]
        )
        
        # Process audio in chunks
        frame_length = porcupine.frame_length
        num_frames = len(audio_array) // frame_length
        
        for i in range(num_frames):
            start = i * frame_length
            end = start + frame_length
            frame = audio_array[start:end]
            
            result = porcupine.process(frame.tolist())
            if result >= 0:
                porcupine.delete()
                return True
        
        porcupine.delete()
        return False
        
    except Exception as e:
        print(f"Error checking wake word: {e}")
        return False
