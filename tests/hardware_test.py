# GitHub für erste Tests und selbst erstellt

import os
import sys
import time
import tempfile

def run():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    print("=" * 50)
    print("KAMERA & MIKROFON TEST")
    print("=" * 50)
    print()

    # ============================================================================
    # TEIL 1: KAMERA TEST
    # ============================================================================
    print("1. KAMERA TEST:")
    print("-" * 50)

    try:
        import cv2
        print("   ✅ OpenCV importiert")
        
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            print("   ✅ Kamera 0 gefunden")
            
            # Test-Bild aufnehmen
            ret, frame = cap.read()
            if ret:
                print(f"   ✅ Bild lesen: {frame.shape[1]}x{frame.shape[0]} Pixel")
                
                # Live-Bild für 3 Sekunden zeigen
                print("   - Zeige Live-Bild (3 Sekunden)...")
                start_time = time.time()
                
                while time.time() - start_time < 3:
                    ret, frame = cap.read()
                    if ret:
                        # Frame spiegeln für intuitivere Ansicht
                        frame = cv2.flip(frame, 1)
                        
                        # Info-Text hinzufügen
                        cv2.putText(frame, "Kamera-Test - ESC zum Ueberspringen", 
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(frame, f"Aufloesung: {frame.shape[1]}x{frame.shape[0]}", 
                                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
                        
                        # Zeit-Anzeige
                        elapsed = int(time.time() - start_time)
                        cv2.putText(frame, f"Zeit: {elapsed}s", 
                                (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1)
                        
                        cv2.imshow("Kamera Test", frame)
                        
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC-Taste
                        print("   Uebersprungen (ESC gedrueckt)")
                        break
                
                cv2.destroyAllWindows()
                print("   ✅ Kamera-Test erfolgreich")
            else:
                print("   ❌ Kamera kann kein Bild lesen")
        else:
            print("   ❌ Kamera 0 nicht verfuegbar")
        
        cap.release()
        
    except ImportError:
        print("   ❌ OpenCV nicht installiert")
        print("   Bitte installieren: pip install opencv-python")
    except Exception as e: 
        print(f"   ❌ Fehler: {e}")


    print("\n" + "=" * 50 + "\n")

    print("2. MIKROFON TEST:")
    print("-" * 50)

    # prüfen, ob sounddevice installiert ist
    try:
        import sounddevice as sd
        print("   ✅ SoundDevice importiert")
        sounddevice_available = True
    except ImportError:
        print("   ❌ SoundDevice nicht installiert")
        print("   Bitte installieren: pip install sounddevice")
        sounddevice_available = False

    if sounddevice_available:
        print("\n2.1 SoundDevice Test:")
        
        try:
            import numpy as np
            print("   ✅ NumPy importiert")
            
            # auflisten der audiogeräte
            print("   - Verfuegbare Audio-Geraete:")
            try:
                devices = sd.query_devices()
                input_devices = []
                
                for i, dev in enumerate(devices):
                    if dev['max_input_channels'] > 0:
                        input_devices.append((i, dev['name']))
                        print(f"     [{i}] {dev['name']}")
                        print(f"         Eingaenge: {dev['max_input_channels']}")
                
                if input_devices:
                    print(f"   ✅ {len(input_devices)} Eingabe-Geraete gefunden")
                    
                    # Test-Aufnahme
                    print("\n   - Test-Aufnahme (2 Sekunden)...")
                    print("     SPRECHE JETZT ETWAS!")
                    
                    samplerate = 16000
                    duration = 2
                    
                    # countdown
                    for i in range(3, 0, -1):
                        print(f"     {i}...")
                        time.sleep(1)
                    
                    print("     AUFNAHME LAEUFT!")
                    
                    # starten der aufnahme
                    recording = sd.rec(int(duration * samplerate),
                                    samplerate=samplerate,
                                    channels=1,
                                    dtype='float32')
                    
                    # warten während aufahme
                    for i in range(duration):
                        time.sleep(1)
                        print(f"     ...{i+1}/{duration}s")
                    
                    sd.wait()  
                    print("     ✅ Aufnahme beendet")
                    
                    # prüfen der aufnahme
                    if recording is not None:
                        print(f"   ✅ Aufnahme erfolgreich: {recording.shape[0]} Samples")
                        
                        # analysierung der lautstärke
                        max_volume = np.max(np.abs(recording))
                        print(f"   - Maximale Lautstaerke: {max_volume:.3f}")
                        
                        if max_volume > 0.01:
                            print("   ✅ Ton erkannt")
                        else:
                            print("   ⚠️  Sehr leiser oder kein Ton")
                    else:
                        print("   ❌ Aufnahme fehlgeschlagen")
                        
                else:
                    print("   ❌ Keine Eingabe-Geraete gefunden")
                    
            except Exception as e:
                print(f"   ❌ Fehler bei Geraeteabfrage: {e}")
                
        except Exception as e:
            print(f"   ❌ Fehler: {e}")

    print("\n2.2 Spracherkennung Test:")
    print("-" * 50)

    # prüfung, ob SpeechRecognition installiert ist
    try:
        import speech_recognition as sr
        print("   ✅ SpeechRecognition importiert")
        speechrecognition_available = True
    except ImportError:
        print("   ❌ SpeechRecognition nicht installiert")
        print("   Bitte installieren: pip install SpeechRecognition")
        speechrecognition_available = False

    if sounddevice_available and speechrecognition_available:
        try:
            import soundfile as sf
            
            r = sr.Recognizer()
            
            print("\n   - Test: Sprache-zu-Text (3 Sekunden)...")
            print("     SPRECHE JETZT AUF DEUTSCH!")
            
            # countdown
            for i in range(3, 0, -1):
                print(f"     {i}...")
                time.sleep(1)
            
            print("     SPRECHE JETZT!")
            
            # aufnahme
            samplerate = 16000
            duration = 3
            
            audio_data = sd.rec(int(duration * samplerate),
                            samplerate=samplerate,
                            channels=1,
                            dtype='float32')
            
            # während der aufnahme
            for i in range(duration):
                time.sleep(1)
                print(f"     ...{i+1}/{duration}s")
            
            sd.wait()
            print("     ✅ Aufnahme beendet")
            
            if audio_data is not None and len(audio_data) > 0:
                
                # erstellung einer temporären WAV-Datei 
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpfile:
                    temp_filename = tmpfile.name
                
                # speichern der audio
                sf.write(temp_filename, audio_data, samplerate)
                print("     Verarbeite Audio...")
                
                # spracherkennung
                try:
                    with sr.AudioFile(temp_filename) as source:
                        audio = r.record(source)
                        
                        try:
                            text = r.recognize_google(audio, language="de-DE")
                            print(f"     ✅ Sprache erkannt: '{text}'")
                        except sr.UnknownValueError:
                            print("     ⚠️  Sprache nicht erkannt")
                        except sr.RequestError:
                            print("     ⚠️  Keine Internetverbindung")
                            
                except Exception as e:
                    print(f"     ❌ Fehler bei Spracherkennung: {e}")
                
                # löschen der temporären WAV-Datei
                try:
                    os.unlink(temp_filename)
                except:
                    pass
            else:
                print("     ❌ Aufnahme fehlgeschlagen")
                
        except Exception as e:
            print(f"   ❌ Fehler: {e}")

    print("\n" + "=" * 50)
    print("=== ERGEBNISZUSAMMENFASSUNG ===")
    print("=" * 50)
    print()
    print("KAMERA:      ✅ Getestet")
    print("MIKROFON:    " + ("✅ Getestet" if sounddevice_available else "❌ Nicht getestet"))
    print("SPRACHE:     " + ("✅ Getestet" if speechrecognition_available else "❌ Nicht getestet"))
    print()
    print("=" * 50)

    # ENDE
    print("\nProgramm erfolgreich beendet.")
    print("Druecke Enter zum Schliessen...")

    try:
        input()
    except:
        pass

    print("See you later, Alligator 🐊")

if __name__ == "__main__":
    run()