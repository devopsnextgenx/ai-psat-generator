import pyaudio
import json
import time
import numpy as np
from vosk import Model, KaldiRecognizer

def detect_silence(audio_data, threshold=500):
    """Detect if the audio segment is silent."""
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    return np.max(np.abs(audio_array)) < threshold

def process_audio(callback=None):
    model = Model("vosk-model")
    recognizer = KaldiRecognizer(model, 16000)
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=4096)
    stream.start_stream()

    print("Waiting for wake word 'bot'...")
    is_listening = False
    captured_audio = []
    last_sound_time = None

    try:
        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if len(data) == 0:
                continue

            # Check for silence if we're already listening
            if is_listening and detect_silence(data):
                if last_sound_time and time.time() - last_sound_time > 2:
                    print("Silence detected, processing audio...")
                    break
            else:
                last_sound_time = time.time()
            
            # Process the current audio chunk
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower().replace("the ", "")
                print(f"Recognized: {is_listening} | {text}")  # Debugging output

                if not is_listening and "alexa" in text:
                    print("Wake word detected! Listening...")
                    is_listening = True
                    captured_audio = [data]
                    print(f"is_listening: {is_listening}")  # Debugging output
                    continue

                if is_listening and ("stop" in text or "terminate" in text):
                    print("Stop word detected! Processing audio...")
                    is_listening = False
                    # Process captured audio for final result
                    if captured_audio:
                        full_recognizer = KaldiRecognizer(model, 16000)
                        for chunk in captured_audio[:-1]:  # Process all chunks except the last one
                            full_recognizer.AcceptWaveform(chunk)
                        final_result = json.loads(full_recognizer.FinalResult()).get("text", "")
                        if callback and final_result:
                            callback(final_result)
                        return final_result
                    break

            # Add data to captured_audio if we're listening
            if is_listening:
                captured_audio.append(data)
            # print(f"captured_audio length: {len(captured_audio)} : {captured_audio}")  # Debugging output
        return ""

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def handle_result(text):
    """Callback function to handle the recognized text."""
    print("Final result:", text)

if __name__ == "__main__":
    process_audio(callback=handle_result)