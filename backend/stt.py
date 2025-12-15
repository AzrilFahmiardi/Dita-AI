import torch
import sounddevice as sd
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import numpy as np
from config_manager import get_stt_config

# Load STT configuration
stt_config = get_stt_config()
MODEL_NAME = stt_config['model_name']
SAMPLE_RATE = stt_config['sample_rate']
DEFAULT_DURATION = stt_config['default_duration']

processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)

def record_audio(duration=None, samplerate=None):
    duration = duration or DEFAULT_DURATION
    samplerate = samplerate or SAMPLE_RATE
    print(f"Merekam selama {duration} detik...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    print("Rekaman selesai.")
    return np.squeeze(audio)

def transcribe_audio(audio_buffer=None, duration=None):
    if audio_buffer is None:
        duration = duration or DEFAULT_DURATION
        audio = record_audio(duration=duration)
    else:
        audio = audio_buffer
    
    inputs = processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt", padding=True)
    
    with torch.no_grad():
        logits = model(inputs.input_values).logits
    
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]
    print("Transkripsi:", transcription.lower())
    return transcription.lower()
