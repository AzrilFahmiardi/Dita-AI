import pyaudio
import numpy as np
import torch
from collections import deque
from config_manager import ConfigManager


class VoiceActivityRecorder:
    def __init__(self, debug=False):
        config = ConfigManager()
        vad_config = config.get_vad_config()
        
        self.sample_rate = vad_config['sample_rate']
        self.channels = vad_config['channels']
        self.threshold = vad_config.get('threshold', 0.5)
        
        self.silence_threshold = vad_config['silence_threshold_seconds']
        self.min_duration = vad_config['min_recording_seconds']
        self.max_duration = vad_config['max_recording_seconds']
        
        self.debug = debug
        
        self.vad_model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        
        self.get_speech_timestamps = utils[0]
        
        self.audio_interface = pyaudio.PyAudio()
        self.chunk_size = 512
        
        self.silence_chunks_threshold = int(self.silence_threshold * self.sample_rate / self.chunk_size)
        self.min_chunks = int(self.min_duration * self.sample_rate / self.chunk_size)
        self.max_chunks = int(self.max_duration * self.sample_rate / self.chunk_size)
        
        if self.debug:
            print(f"VAD Configuration:")
            print(f"  Model: Silero VAD")
            print(f"  Sample rate: {self.sample_rate} Hz")
            print(f"  Chunk size: {self.chunk_size}")
            print(f"  Threshold: {self.threshold}")
            print(f"  Silence threshold: {self.silence_threshold}s ({self.silence_chunks_threshold} chunks)")
            print(f"  Min duration: {self.min_duration}s ({self.min_chunks} chunks)")
            print(f"  Max duration: {self.max_duration}s ({self.max_chunks} chunks)")
    
    def record(self):
        stream = self.audio_interface.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        print("Mendengarkan...")
        
        audio_chunks = []
        voice_detected = False
        silent_chunks = 0
        total_chunks = 0
        speech_chunks = 0
        
        try:
            while True:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_int16 = np.frombuffer(data, dtype=np.int16)
                audio_float32 = audio_int16.astype(np.float32) / 32768.0
                
                audio_tensor = torch.from_numpy(audio_float32)
                speech_prob = self.vad_model(audio_tensor, self.sample_rate).item()
                
                is_speech = speech_prob > self.threshold
                
                if not voice_detected:
                    if is_speech:
                        voice_detected = True
                        print("Suara terdeteksi, mulai merekam...")
                        if self.debug:
                            print(f"  Speech probability: {speech_prob:.3f}")
                        audio_chunks.append(audio_float32)
                        total_chunks += 1
                        speech_chunks += 1
                else:
                    audio_chunks.append(audio_float32)
                    total_chunks += 1
                    
                    if is_speech:
                        speech_chunks += 1
                        silent_chunks = 0
                        if self.debug and total_chunks % 50 == 0:
                            duration = total_chunks * self.chunk_size / self.sample_rate
                            print(f"  Recording... {duration:.1f}s (speech: {speech_chunks}, prob: {speech_prob:.3f})")
                    else:
                        silent_chunks += 1
                        if self.debug and silent_chunks in [20, 40, 60]:
                            print(f"  Silence: {silent_chunks}/{self.silence_chunks_threshold} chunks (prob: {speech_prob:.3f})")
                    
                    if silent_chunks >= self.silence_chunks_threshold:
                        if total_chunks >= self.min_chunks:
                            duration = total_chunks * self.chunk_size / self.sample_rate
                            print(f"Pengguna berhenti bicara (silence: {silent_chunks} chunks)")
                            print(f"Total duration: {duration:.2f}s")
                            break
                    
                    if total_chunks >= self.max_chunks:
                        print("Durasi maksimal tercapai, menghentikan rekaman...")
                        break
                    
        finally:
            stream.stop_stream()
            stream.close()
        
        if not voice_detected:
            print("Tidak ada suara terdeteksi")
            return np.array([], dtype=np.float32)
        
        audio_array = np.concatenate(audio_chunks)
        return audio_array
    
    def close(self):
        self.audio_interface.terminate()
