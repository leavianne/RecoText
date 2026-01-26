# Grundgerüst bereitgestellt von Herr Kammer (Basierend auf GitHub und ChatGpt): Emotiontracker 
# und selbstständig optimiert und mit Emojis verbunden

import os
import time

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
tf.get_logger().setLevel('ERROR')
tf.autograph.set_verbosity(0)

import logging
logging.getLogger('deepface').setLevel(logging.ERROR)
logging.getLogger('tensorflow').setLevel(logging.ERROR)

import cv2
from deepface import DeepFace
import numpy as np
import sys

EMOJI_MAP = {
    "angry": "😠",
    "disgust": "🤢",
    "fear": "😨",
    "happy": "😄",
    "sad": "😢",
    "surprise": "😲",
    "neutral": "😐"
}

# Optimierungs-Parameter
FRAME_SKIP=5            # DeepFace nur alle N Frames ausführen
MOTION_THRESHOLD=500    # Bewegungsschwelle (Background Subtraction)
ROI_SIZE=(224,224)      # Eingabegröße für DeepFace
STABILITY_DISTANCE=20   # Mindestbewegung des Gesichts (Pixel)
STABLE_DURATION = 1.5   # Sekunden für stabile Emotion

# Fortschrittsbalken
BAR_WIDTH = 200
BAR_HEIGHT = 15

# Initialisierung
face_cascade=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
cap=cv2.VideoCapture(0)
backsub=cv2.createBackgroundSubtractorMOG2(history=200,varThreshold=25)

last_face_center=None     # letzte bekannte Position des Gesichts
cached_emotion="..."      # zwischengespeicherte Emotion
last_emotion_time = None
frame_count=0
stable_emotion = None

cv2.namedWindow("Emotions-Erkennung mit Emojis", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Emotions-Erkennung mit Emojis", 640, 480)
cv2.setWindowProperty("Emotions-Erkennung mit Emojis", cv2.WND_PROP_TOPMOST, 1)

# Hauptschleife
while True:
    ret,frame=cap.read()
    if not ret:
        break
    frame_count+=1
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    h_frame, w_frame = frame.shape[:2]

    cv2.rectangle(frame, (0, h_frame-70), (250, h_frame), (255, 255, 255), -1)

    # Bewegungserkennung
    fgmask=backsub.apply(gray)
    _,motion_mask=cv2.threshold(fgmask,200,255,cv2.THRESH_BINARY)
    motion_detected=cv2.countNonZero(motion_mask)>MOTION_THRESHOLD

    # Gesichtserkennung (nur größtes Gesicht)
    faces=face_cascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(40,40))
    if len(faces)>0:
        faces=[max(faces,key=lambda f:f[2]*f[3])]

    # Tracking & Emotion
    for (x,y,w,h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
        face_center=(x+w//2,y+h//2)

        # Prüfen, ob sich das Gesicht deutlich bewegt hat
        face_moved=True
        if last_face_center is not None:
            dist=np.linalg.norm(np.array(face_center)-np.array(last_face_center))
            face_moved=dist>STABILITY_DISTANCE

        # DeepFace nur bei Bedarf ausführen
        should_analyze=face_moved or motion_detected or (frame_count%FRAME_SKIP==0)
        if should_analyze:
            face_roi=cv2.resize(frame[y:y+h,x:x+w],ROI_SIZE)
            try:
                result=DeepFace.analyze(face_roi,actions=['emotion'],enforce_detection=False)
                emotion=result[0]['dominant_emotion']
                cached_emotion = emotion
                last_face_center=face_center
            except:
                emotion = cached_emotion
        # Stable-Check
        if stable_emotion == emotion:
            if time.time() - last_emotion_time >= STABLE_DURATION:
                filled_width = BAR_WIDTH
                cap.release()
                cv2.destroyAllWindows()
                print(f"Stable Emotion erkannt: {emotion}")
                detected_emoji = emotion
        else:
            stable_emotion = emotion
            last_emotion_time = time.time() 

        # Fortschrittsbalken
        progress_ratio = 0.0
        if last_emotion_time is not None:
            elapsed = time.time() - last_emotion_time
            progress_ratio = min(elapsed / STABLE_DURATION, 1.0)

        filled_width = int(BAR_WIDTH * progress_ratio)

        bar_x = 10
        bar_y = h_frame - 35

        # Hintergrund (leer)
        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + BAR_WIDTH, bar_y + BAR_HEIGHT),
            (180, 180, 180),
            -1
        )

        # Fortschritt (gefüllt)
        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + filled_width, bar_y + BAR_HEIGHT),
            (0, 200, 0),
            -1
        )

        # Rahmen
        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + BAR_WIDTH, bar_y + BAR_HEIGHT),
            (0, 0, 0),
            2
        )

        # Geste als Text darüber
        cv2.putText(
            frame,
            cached_emotion,
            (bar_x, bar_y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            2
        )

        # Anzeige der letzten bekannten Emotion
        emoji_display = EMOJI_MAP.get(cached_emotion, "")
        cv2.putText(frame,cached_emotion,(x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Anzeige & Beenden
    cv2.imshow("Emotions-Erkennung mit Emojis",frame)
    if cv2.waitKey(1)&0xFF == 27:  # ESC
        print("\nProgramm manuell beendet")
        break

cap.release()
cv2.destroyAllWindows()

if detected_emoji:
    print(detected_emoji)
    sys.exit(0)
else:
    print("ERROR: Kein Emoji erkannt")
    sys.exit(1)