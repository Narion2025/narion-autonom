import os
import time
import json
import requests
from datetime import datetime
from twilio.rest import Client

TRIGGER_URL = "https://wirklichkeits-api.onrender.com/status"
POLL_INTERVAL = 5
LOG_FILE = "trigger.log"

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_TO = os.getenv("TWILIO_TO_NUMBER")

twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)
    print(line.strip())

def handle_trigger(data):
    trigger = data.get("trigger")
    params = data.get("params", {})
    if trigger == "sende_SMS":
        message = params.get("message", "Kein Text.")
        to = params.get("to", TWILIO_TO)
        try:
            twilio_client.messages.create(
                body=message,
                from_=TWILIO_FROM,
                to=to
            )
            log(f"📩 SMS gesendet an {to}: {message}")
        except Exception as e:
            log(f"❌ Fehler beim Senden: {e}")
    else:
        log(f"⚠️ Unbekannter Trigger: {trigger}")

def poll_trigger():
    log("🌐 Online-Überwachung läuft...")
    last_data = None
    while True:
        try:
            response = requests.get(TRIGGER_URL)
            if response.status_code == 200:
                data = response.json()
                if data != last_data:
                    handle_trigger(data)
                    last_data = data
        except Exception as e:
            log(f"Fehler bei Abruf: {e}")
        time.sleep(POLL_INTERVAL)

poll_trigger()
