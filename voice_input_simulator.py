import sys
import os
import argparse
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from redis_bus import RedisBus

def simulate_voice_input(text_command):
    bus = RedisBus()
    if not bus.connect():
        print("❌ Could not connect to Redis. Ensure Docker is running.")
        return

    print(f"🎙️ Simulating Voice Input: '{text_command}'")
    
    # Payload matching the blueprint structure
    payload = {
        "source": "iphone_manual",
        "transcribed_text": text_command,
        "timestamp": time.time(),
        "user": "Maurice"
    }
    
    bus.publish("input/voice", payload)
    print("✅ Command sent to Orchestrator via Redis channel 'input/voice'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate iPhone Voice Input")
    parser.add_argument("command", type=str, help="The voice command text", nargs="?", default="Erstelle einen TikTok Post über AI Automation")
    args = parser.parse_args()
    
    simulate_voice_input(args.command)
