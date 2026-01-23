# Größtenteils eigenständig erstellt
# Verknüpfung von mit html und Server mit KI erstellt

from pathlib import Path
import webbrowser
import sys
import subprocess
import codecs
import threading

from tests.hardware_test import run as run_hardware_test

if sys.platform == "win32":
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

def run_messenger_html():
    server_file = Path(__file__).parent / "examples" / "messenger" / "server.py"
    def open_browser():
        webbrowser.open("http://127.0.0.1:5000")
    threading.Thread(target=open_browser, daemon=True).start()
    subprocess.run([sys.executable, str(server_file)]) # Server starten

def main():
    print("="*50)
    print("MESSENGER APP")
    print("="*50)

    while True:
        try:
            print("\nVERFÜGBARE OPTIONEN:")
            print("1. HTML im Browser öffnen")
            print("2. Hardware Test ausführen")
            print("0. Beenden")
            
            var = input("\nMenü (0-2): ").strip()
            if var == "1":
                run_messenger_html()          
            elif var == "2":
                print("\nStarte Hardware Test...")
                try:
                    run_hardware_test()
                except ImportError:
                    print("Fehler: Hardware Test nicht verfügbar")
            elif var == "0":
                print("\nProgramm beendet")
                return
            else:
                print("!!! Ungültige Auswahl !!!") 
        except KeyboardInterrupt:
            print("\n\nProgramm beendet")
            return
        except Exception as e:
            print(f"Fehler: {e}")

if __name__ == "__main__":
    main()