# Selbst erstellt, GitHub und KI zur Fehlerbehebung

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import urllib.request
import os
import numpy as np
import sys
import codecs

# UTF-8 Unterstützung für Windows
if sys.platform == "win32":
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')
    import locale
    locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

# Umgebungsvariablen für weniger Logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'
os.environ['OPENCV_LOG_LEVEL'] = 'FATAL'

finger_names = ['Daumen', 'Zeige', 'Mittel', 'Ring', 'Klein']

print("\nStarte Handzeichen-Erkennung...")

print("\nPrüfe Modell-Datei...")
model_file = "hand_landmarker.task"

if not os.path.exists(model_file):
    print("Lade Modell herunter...")
    try:
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        urllib.request.urlretrieve(url, model_file)
        print(f"Modell heruntergeladen")
    except Exception as e:
        print(f"Download fehlgeschlagen: {e}")
        print("Versuche ohne lokale Datei...")
        model_file = None
else:
    print(f"Modell vorhanden")

# MediaPipe Hand Landmarker initialisieren
print("\nInitialisiere Hand-Erkennung...")

try:
    if model_file and os.path.exists(model_file):
        base_options = python.BaseOptions(model_asset_path=model_file)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6
        )
        print("Mit lokaler Datei initialisiert")
    else:
        options = vision.HandLandmarkerOptions(
            num_hands=1,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6
        )
        print("Ohne lokaler Datei initialisiert")
    
    detector = vision.HandLandmarker.create_from_options(options)
    print("Hand-Erkennung bereit")
    
except Exception as e:
    print(f"MediaPipe Fehler: {e}")
    print("\nManuelle Installation der Modell-Datei erforderlich!")
    print("https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task")
    print("Als 'hand_landmarker.task' im gleichen Ordner speichern")
    exit(1)

print("\nÖffne Kamera...")

cap = None
for i in range(2):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, test_frame = cap.read()
        if ret and test_frame is not None:
            print(f"Kamera {i} gefunden")
            break
        else:
            cap.release()
            cap = None

if cap is None or not cap.isOpened():
    print("Keine Kamera gefunden!")
    exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cv2.namedWindow("Handzeichen-Erkennung mit Emojis", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Handzeichen-Erkennung mit Emojis", cv2.WND_PROP_TOPMOST, 1)


print("\nStarte Handerkennung...\n")

def is_finger_extended(tip, pip, mcp, is_thumb=False):
    # Prüft ob ein Finger ausgestreckt ist
    if is_thumb:
        return tip.y < mcp.y - 0.03
    else:
        return tip.y < pip.y - 0.05

def is_fist_hand(hand_landmarks):
    # Prüft ob die Hand eine Faust ist (alle Finger gefaltet)
    tips = [hand_landmarks[i] for i in [8, 12, 16, 20]]
    pips = [hand_landmarks[i] for i in [6, 10, 14, 18]]
    folded_count = 0
    for tip, pip in zip(tips, pips):
        if tip.y > pip.y:
            folded_count += 1
    return folded_count == 4

def analyze_hand_gesture(hand_landmarks):
    # Finger erkennen
    finger_points = [
        [4, 3, 2, True],   # Daumen
        [8, 6, 5, False],  # Zeigefinger
        [12, 10, 9, False], # Mittelfinger
        [16, 14, 13, False], # Ringfinger
        [20, 18, 17, False]  # Kleiner Finger
    ]
    
    extended_fingers = []
    
    for i, (tip_idx, pip_idx, mcp_idx, is_thumb) in enumerate(finger_points):
        tip = hand_landmarks[tip_idx]
        pip = hand_landmarks[pip_idx]
        mcp = hand_landmarks[mcp_idx]
        
        if is_finger_extended(tip, pip, mcp, is_thumb):
            extended_fingers.append(finger_names[i])
    
    fist_detected = is_fist_hand(hand_landmarks)
    
    if fist_detected:
        # Faust erkannt - test ob Daumen ausgestreckt
        thumb_tip = hand_landmarks[4]
        thumb_mcp = hand_landmarks[2]
        
        if is_finger_extended(thumb_tip, hand_landmarks[3], thumb_mcp, True):
            gesture = "Daumen hoch"
            emoji = "👍"
        else:
            gesture = "Faust"
            emoji = "👊"
    else:
        # Normale Gesten
        finger_count = len([f for f in extended_fingers if f != 'Daumen'])
        thumb_extended = 'Daumen' in extended_fingers
        
        # Geste bestimmen
        if finger_count == 0:
            gesture = "Faust" if not thumb_extended else "Daumen hoch"
            emoji = "👊" if not thumb_extended else "👍"
        elif finger_count == 1:
            gesture = "1 Finger"
            emoji = "🖕"
        elif finger_count == 2:
            gesture = "Peace"
            emoji = "✌️"
        elif finger_count == 3:
            gesture = "3 Finger"
            emoji = "👌"
        elif finger_count == 4:
            gesture = "Offene Hand"
            emoji = "🖐️"
        else:
            gesture = f"{finger_count} Finger"
            emoji = "🖐️"
    
    return gesture, emoji, fist_detected, extended_fingers

# Hauptschleife zur Videoverarbeitung - zwei Sekunden stabile Geste erkennen
last_gesture = ""
detected_emoji = None
gesture_start_time = None
GESTURE_CONFIRM_TIME = 2.0

# Optimierte Variablen für Performance
frame_count = 0
start_time = time.time()
last_fps_time = start_time
fps_display = 0
emoji_confirmed = False

print("\nStarte Video-Erkennung...")
print(f"Halte eine Geste 2 Sekunden stabil zum Bestätigen")
print("ESC zum manuellen Beenden")

try:
    while True:
        # Frame lesen
        ret, frame = cap.read()
        if not ret:
            print("Frame nicht lesbar")
            break
        
        frame_count += 1
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        
        # FPS Berechnung
        if frame_count % 15 == 0:
            current_time = time.time()
            if current_time > last_fps_time:
                fps_display = int(15 / (current_time - last_fps_time))
                last_fps_time = current_time
        
        # MediaPipe Verarbeitung
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            result = detector.detect(mp_image)
        except Exception as e:
            print(f"Erkennungsfehler: {e}")
            result = None
        
        cv2.rectangle(frame, (0, 0), (w, 40), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, h-70), (250, h), (255, 255, 255), -1)
        cv2.putText(frame, "HANDZEICHEN-ERKENNUNG", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        if result and result.hand_landmarks:
            hand_landmarks = result.hand_landmarks[0]
            gesture, emoji, fist_detected, extended_fingers = analyze_hand_gesture(hand_landmarks)
            finger_count = len([f for f in extended_fingers if f != 'Daumen'])
            current_time = time.time()
            
            if gesture == last_gesture:
                if gesture_start_time is None:
                    gesture_start_time = current_time

                # Berechne stabile Zeit
                stable_time = current_time - gesture_start_time
                
                # Prüfe ob Geste seit zwei Sekunden stabil ist
                if stable_time >= GESTURE_CONFIRM_TIME and not emoji_confirmed:
                    detected_emoji = emoji
                    emoji_confirmed = True
                    print(f"\nEmoji bestätigt: {emoji} ({gesture})")
                    print("Kamera wird geschlossen...")
                    time.sleep(0.5)
                    break
            else:
                # Neue Geste erkannt, Zeit zurücksetzen
                last_gesture = gesture
                gesture_start_time = current_time
                emoji_confirmed = False
            
            # Hand-Landmarks zeichnen
            finger_tip_indices = [4, 8, 12, 16, 20]
            for idx in finger_tip_indices:
                tip = hand_landmarks[idx]
                x, y = int(tip.x * w), int(tip.y * h)
                cv2.circle(frame, (x, y), 6, (0, 255, 255), -1)
            
            if gesture_start_time is not None:
                stable_time = current_time - gesture_start_time
                
                if emoji_confirmed:
                    # Geste wurde bestätigt
                    cv2.putText(frame, f"{gesture} ✓ BESTÄTIGT", (10, h-40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                    cv2.putText(frame, "Schließe Kamera...", (10, h-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
                    
                elif stable_time < GESTURE_CONFIRM_TIME:
                    # Zeige Countdown
                    time_left = GESTURE_CONFIRM_TIME - stable_time
                    progress = int((stable_time / GESTURE_CONFIRM_TIME) * 100)
                    cv2.putText(frame, f"{gesture} ({progress}%)", (10, h-40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                    cv2.putText(frame, f"Noch {time_left:.1f}s", (10, h-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
                    
                else:
                    cv2.putText(frame, f"{gesture} ✓", (10, h-40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                    cv2.putText(frame, f"Finger: {finger_count}", (10, h-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
                    
            else:
                cv2.putText(frame, f"{gesture}", (10, h-40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                cv2.putText(frame, f"Finger: {finger_count}", (10, h-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
                
        else:
            # Keine Hand erkannt
            cv2.putText(frame, "KEINE HAND ERKANNT", (w//2-120, h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            last_gesture = ""
            gesture_start_time = None
            emoji_confirmed = False
        
        # Steuerung anzeigen (unten rechts)
        cv2.putText(frame, "ESC: Beenden", (w-120, h-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Fenster anzeigen
        cv2.imshow("Handzeichen-Erkennung mit Emojis", frame)
        
        # Tastendruck prüfen
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            print("\nProgramm manuell beendet")
            break
        
        # Fenster prüfen
        if cv2.getWindowProperty("Handzeichen-Erkennung mit Emojis", cv2.WND_PROP_VISIBLE) < 1:
            print("\nFenster geschlossen")
            break
            
        # Schleife beenden, wenn Emoji erkannt wurde
        if emoji_confirmed:
            break

except KeyboardInterrupt:
    print("\nProgramm durch Benutzer unterbrochen")
except Exception as e:
    print(f"\nFehler: {e}")
    import traceback
    traceback.print_exc()

if cap:
    cap.release()
cv2.destroyAllWindows()

print("\n" + "=" * 50)
print("ERKENNUNGSERGEBNIS")
print("=" * 50)

if detected_emoji:
    emoji_to_gesture = {
        "👊": "Faust",
        "👍": "Daumen hoch", 
        "🖕": "1 Finger",
        "✌️": "Peace-Zeichen",
        "👌": "OK-Handzeichen",
        "🖐️": "Offene Hand"
    }
    gesture_name = emoji_to_gesture.get(detected_emoji, "Unbekannte Geste")
    
    print(f"Erfolgreich erkannt!")
    print(f"Emoji: {detected_emoji}")
    print(f"Geste: {gesture_name}")
    print(f"Erkennungszeit: {GESTURE_CONFIRM_TIME} Sekunden")
else:
    print("Kein Emoji wurde erfolgreich erkannt")
    print("Halte eine Geste 2 Sekunden stabil vor der Kamera")

runtime = time.time() - start_time
print(f"\nProgramm-Laufzeit: {runtime:.1f}s")
print(f"Verarbeitete Frames: {frame_count}")

if detected_emoji:
    print(detected_emoji)
    sys.exit(0)
else:
    print("ERROR: Kein Emoji erkannt")
    sys.exit(1)