# Grundgerüst und flask mit KI erstellt 
# -> Funktion für Server-Spracherkennung größtenteils KI weitere Funktionen sebstständig 
# händig erweitert

from flask import Flask, send_from_directory, jsonify
from pathlib import Path
import subprocess
import sys

app = Flask(__name__)
BASE_DIR = Path(__file__).parent

# =========================
# FRONTEND AUSLIEFERN
# =========================
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/<path:filename>")
def serve_file(filename):
    return send_from_directory(BASE_DIR, filename)

# =========================
# EMOJI-ERKENNUNG (Hand)
# =========================
@app.route("/recognize-emoji", methods=["POST"])
def recognize_emoji():
    try:
        script_path = BASE_DIR.parent.parent / "src" / "emoji.py"
        if not script_path.exists():
            return jsonify({
                "status": "error", 
                "message": f"emoji.py nicht gefunden unter {script_path}"
            }), 404
        
        print(f"Starte Emoji-Erkennung: {script_path}")
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=35
        )
        
        print(f"Emoji-Prozess beendet mit Code: {result.returncode}")
        
        if result.returncode == 0:
            output_lines = result.stdout.split('\n')
            recognized_emoji = ""
            emoji_indicators = [
                "Programm beendet. Erkanntes Emoji:",
                "Erkanntes Emoji:",
                "Emoji:",
                "Emoji:"
            ]
            
            for line in output_lines:
                for indicator in emoji_indicators:
                    if indicator in line:
                        parts = line.split(indicator)
                        if len(parts) > 1:
                            emoji = parts[1].strip()
                            if emoji:
                                emoji = emoji.strip("'\"")
                                if emoji:
                                    recognized_emoji = emoji[0] if emoji[0] != ' ' else emoji[1] if len(emoji) > 1 else ""
                                break
                
                if not recognized_emoji:
                    for char in line:
                        if ord(char) >= 0x1F300 and ord(char) <= 0x1F9FF:
                            recognized_emoji = char
                            break
            
            if not recognized_emoji:
                emoji_map = {
                    "Faust": "👊",
                    "Daumen hoch": "👍",
                    "1 Finger": "🖕",
                    "Peace": "✌️",
                    "3 Finger": "👌",
                    "Offene Hand": "🖐️"
                }
                
                for line in output_lines:
                    for text, emoji in emoji_map.items():
                        if text in line and "Geste:" in line:
                            recognized_emoji = emoji
                            break
                    if recognized_emoji:
                        break
            
            if not recognized_emoji:
                for line in reversed(output_lines):
                    line = line.strip()
                    if line and ("✅" in line or "🎯" in line):
                        for char in line:
                            if ord(char) >= 0x1F300 and ord(char) <= 0x1F9FF:
                                recognized_emoji = char
                                break
                        if recognized_emoji:
                            break
            
            print(f"Emoji erkannt: '{recognized_emoji}'")
            
            if recognized_emoji:
                # Wandle Text-Emoji in Unicode-Emoji um
                emoji_conversion = {
                    "👊": "👊",
                    "👍": "👍",
                    "🖕": "🖕",
                    "✌️": "✌️",
                    "👌": "👌",
                    "🖐️": "🖐️",
                    "❓": "❓"
                }
                
                final_emoji = emoji_conversion.get(recognized_emoji, recognized_emoji)
                
                return jsonify({
                    "status": "success",
                    "emoji": final_emoji,
                    "text": f"Erkannte Geste: {final_emoji}"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Kein Emoji erkannt"
                })
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unbekannter Fehler"
            print(f"Fehler: {error_msg}")
            return jsonify({
                "status": "error",
                "message": f"Prozessfehler: {error_msg}"
            }), 500
            
    except subprocess.TimeoutExpired:
        print("Timeout bei Emoji-Erkennung")
        return jsonify({
            "status": "error",
            "message": "Emoji-Erkennung dauerte zu lange (Timeout)"
        }), 408
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    

# =========================
# EMOJI-ERKENNUNG (Gesicht)
# =========================
@app.route("/recognize-face", methods=["POST"])
def recognize_face():
    """Startet die Gesichtserkennung und gibt Emoji zurück"""
    try:
        script_path = BASE_DIR.parent.parent / "src" / "emotionen.py"
        
        print(f"Gesichtserkennung Pfad: {script_path}")
        
        if not script_path.exists():
            return jsonify({
                "status": "error", 
                "message": f"emotionen.py nicht gefunden"
            }), 404
        
        # Gesichtserkennung starten
        print("Starte Gesichtserkennung...")
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=35
        )
        
        print(f"Prozess beendet mit Code: {result.returncode}")
        
        print(f"STDOUT Länge: {len(result.stdout)}")
        print(f"STDERR Länge: {len(result.stderr)}")

        output = result.stdout.strip()
        error_output = result.stderr.strip()

        if result.returncode == 0 and output:
            emoji = None
            import re 
            emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF]')
            emoji_match = emoji_pattern.search(output)

            if emoji_match:
                emoji = emoji_match.group()

            else:
                # Fallback: Prüfe auf spezifische Meldungen
                if "happy" in output.lower():
                    emoji = "😄"
                elif "sad" in output.lower():
                    emoji = "😢"
                elif "angry" in output.lower():
                    emoji = "😠"
                elif "surprise" in output.lower():
                    emoji = "😲"
                elif "neutral" in output.lower():
                    emoji = "😐"
                elif "fear" in output.lower():
                    emoji = "😨"
                elif "disgust" in output.lower():
                    emoji = "🤢"
            
            if emoji:
                return jsonify({
                    "status": "success",
                    "emoji": emoji,
                    "text": f"Emotion erkannt: {emoji}"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Keine Emotion erkannt. Output: {output[:50]}"
                })
        else:
            error_msg = error_output if error_output else output if output else "Unbekannter Fehler"
            return jsonify({
                "status": "error",
                "message": f"Fehler: {error_msg[:100]}"
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "error",
            "message": "Gesichtserkennung dauerte zu lange"
        }), 408
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
# =========================
# SPRACHERKENNUNG
# =========================
@app.route("/voice-transcribe", methods=["POST"])
def voice_transcribe():
    """Startet die Spracherkennung und gibt den Text zurück"""
    try:
        script_path = BASE_DIR.parent.parent / "src" / "spracherkennung.py"
        
        print(f"Spracherkennung Pfad: {script_path}")
        
        if not script_path.exists():
            return jsonify({
                "status": "error", 
                "message": f"spracherkennung.py nicht gefunden"
            }), 404
        
        # Spracherkennung starten
        print("Starte Spracherkennung...")
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=35
        )
        
        print(f"Prozess beendet mit Code: {result.returncode}")
        print(f"STDOUT Länge: {len(result.stdout)}")
        print(f"STDERR Länge: {len(result.stderr)}")

        recognized_text = result.stdout.strip()
        if recognized_text and not recognized_text.startswith("ERROR:"):
            print(f"Erkannten Text: '{recognized_text}'")
            return jsonify({
                "status": "success",
                "text": recognized_text
            })
        else:
            # Fehlerbehandlung
            error_message = "Keine Sprache erkannt"
            if recognized_text.startswith("ERROR:"):
                error_message = recognized_text.replace("ERROR:", "").strip()
            elif result.stderr:
                for line in result.stderr.split('\n'):
                    if "Fehler" in line or "Nichts" in line:
                        error_message = line.replace("Fehler", "").strip()
                        break
            
            print(f"Fehler: {error_message}")
            return jsonify({
                "status": "error",
                "message": error_message
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "error",
            "message": "Spracherkennung dauerte zu lange"
        }), 408
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)