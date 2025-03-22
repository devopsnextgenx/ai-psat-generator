import asyncio
import io
from edge_tts import Communicate
import sounddevice as sd
import soundfile as sf
from collections import deque
import time
import threading
from queue import Queue
import nest_asyncio
import wave
import json
from vosk import Model, KaldiRecognizer

model = Model("vosk-model")

# Enable nested event loops
nest_asyncio.apply()

class TTSQueue:
    def __init__(self, status_callback=None):
        self.queue = deque()
        self.is_playing = False
        self.pause_duration = 0.15
        self.should_stop = False
        self._thread = None
        self._loop = None
        self.status_callback = status_callback  # Add status callback
        
    def add_text(self, text, voice="en-US-JennyNeural"):
        """Add text to the queue"""
        print(f"{text}")
        self.queue.append({"text": text, "voice": voice})
        
    def start_processing(self):
        """Start processing in a separate thread"""
        if self._thread is None or not self._thread.is_alive():
            self.should_stop = False
            self._thread = threading.Thread(target=self._run_async_loop, daemon=True)
            self._thread.start()
    
    def stop_processing(self):
        """Stop processing the queue"""
        self.should_stop = True
        if self._thread and self._thread.is_alive():
            self._thread.join()
            
    def _run_async_loop(self):
        """Run the async event loop in the thread"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self.process_queue())
        
    def _safe_callback(self, is_playing):
        """Safely execute the status callback"""
        if self.status_callback:
            try:
                asyncio.get_event_loop().call_soon_threadsafe(self.status_callback, is_playing)
            except Exception as e:
                print(f"Warning: Status callback failed: {str(e)}")
                
    async def process_queue(self):
        """Process all items in the queue"""
        self.is_playing = True
        self._safe_callback(self.is_playing)
        
        while not self.should_stop:
            if self.queue:
                item = self.queue.popleft()
                await self.text_to_speech(item["text"], item["voice"])
                time.sleep(self.pause_duration)
            else:
                await asyncio.sleep(0.1)
                
        self.is_playing = False
        self._safe_callback(self.is_playing)

    async def text_to_speech(self, text, voice="en-US-ChristopherNeural"):
        """Convert text to speech and play it directly"""
        try:
            communicate = Communicate(text, voice)
            audio_buffer = io.BytesIO()
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])
            
            audio_buffer.seek(0)
            audio_data, sample_rate = sf.read(audio_buffer)
            sd.play(audio_data, sample_rate)
            sd.wait()
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")

# Example usage
def main():
    # Create TTS queue instance
    tts_queue = TTSQueue()
    
    # Start processing in separate thread
    tts_queue.start_processing()
    
    # Simulate other work while TTS is running
    print("Main thread can do other work...")
    
    # Add texts to queue
    tts_queue.add_text("Hello! This is the first sentence.", "en-US-JennyNeural")
    time.sleep(1)  # Simulate some work
    print("Adding second sentence...")
    tts_queue.add_text("This is the second sentence.", "en-US-JennyNeural")
    time.sleep(1)  # Simulate some work
    print("Adding third sentence...")
    tts_queue.add_text("And this is the third sentence.", "en-US-JennyNeural")
    
    # Let the program run for a while
    time.sleep(10)
    
    # Stop the TTS queue
    print("Stopping TTS queue...")
    tts_queue.stop_processing()

if __name__ == "__main__":
    main()