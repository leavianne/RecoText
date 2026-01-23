# GitHub, erweitert mit KI

import sounddevice as sd
import speech_recognition as sr
import numpy as np
import time
import sys

class SpeechRecognizer:
    def __init__(self, silence_threshold=0.01, silence_time=3.0):
        self.silence_time = 4.0
        self.silence_threshold = silence_threshold
        self.silence_time = silence_time
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_duration = 0.1
        
    def record_until_silence(self):
        audio_chunks = []
        silence_counter = 0
        
        def callback(indata, frames, time_info, status):
            nonlocal silence_counter
            chunk = indata.copy()
            
            # Stille erkennen
            volume = np.max(np.abs(chunk))
            if volume < self.silence_threshold:
                silence_counter += self.chunk_duration
            else:
                silence_counter = 0
            audio_chunks.append(chunk)
        
        try:
            stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback,
                blocksize=int(self.sample_rate * self.chunk_duration),
                dtype='float32'
            )
            
            with stream:
                print("Sprechen Sie jetzt", file=sys.stderr)
                while silence_counter < self.silence_time:
                    time.sleep(0.1)
                time.sleep(0.1)
            
            # Letzte Stille entfernen
            chunks_to_remove = int((self.silence_time / self.chunk_duration))
            if len(audio_chunks) > chunks_to_remove:
                audio_chunks = audio_chunks[:-chunks_to_remove]
            
            if audio_chunks:
                audio_data = np.concatenate(audio_chunks)
                print(f"{len(audio_data)/self.sample_rate:.1f}s Audio aufgenommen", file=sys.stderr)
                return audio_data
            return None
            
        except Exception as e:
            print(f"Fehler bei Aufnahme: {e}", file=sys.stderr)
            return None
    
    def transcribe_audio(self, audio_data):
        try:
            recognizer = sr.Recognizer()
            audio_normalized = audio_data.flatten()
            audio_int16 = (audio_normalized * 32767).astype(np.int16)
            audio_bytes = audio_int16.tobytes()
            audio_for_recognition = sr.AudioData(
                audio_bytes, 
                self.sample_rate, 
                2
            )
            
            print("Analysiere Sprache...", file=sys.stderr)
            text = recognizer.recognize_google(
                audio_for_recognition, 
                language="de-DE",
                show_all=False
            )
            
            if text and text.strip():
                print(f"Erkannt: {text}", file=sys.stderr)
                return text.strip()
            return None
            
        except sr.UnknownValueError:
            print("Keine verständliche Sprache erkannt", file=sys.stderr)
            return None
        except sr.RequestError as e:
            print(f"API-Fehler: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Fehler bei Transkription: {e}", file=sys.stderr)
            return None
    
    def recognize(self):
        try:
            print("="*50, file=sys.stderr)
            print("SPRACHERKENNUNG", file=sys.stderr)
            print("="*50, file=sys.stderr)
            
            # Audio aufnehmen
            audio_data = self.record_until_silence()
            
            if audio_data is not None:
                text = self.transcribe_audio(audio_data)
                return text
            else:
                print("Kein Audio aufgenommen", file=sys.stderr)
                return None
                
        except KeyboardInterrupt:
            print("\nAufnahme abgebrochen", file=sys.stderr)
            return None
        except Exception as e:
            print(f"\nFehler: {e}", file=sys.stderr)
            return None

def main():
    recognizer = SpeechRecognizer()
    result = recognizer.recognize()
    
    if result:
        print(result)
    else:
        print("ERROR: Keine Sprache erkannt")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)