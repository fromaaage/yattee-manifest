#!/usr/bin/env python3

import json
import os
import requests
import subprocess
from time import sleep

# Konfiguration
MANIFEST_PATH = "piped_manifest.json"
MIN_SCORE = 3
TEST_ENDPOINTS = [
    "/api/v1/search?q=test",
    "/api/v1/streams/abc123",
    "/api/v1/channels/UC_x5XG1OV2P6uZZ5FSM9Ttw",
    "/api/v1/suggestions?q=test"
]

HEADERS = {
    "User-Agent": "Yattee",
    "Accept": "application/json"
}

def test_instance(base_url):
    working = 0
    total_time = 0.0
    for endpoint in TEST_ENDPOINTS:
        url = base_url + endpoint
        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
            if response.status_code in [200, 400, 404]:
                working += 1
                total_time += response.elapsed.total_seconds()
        except requests.RequestException:
            continue
    return working, total_time / len(TEST_ENDPOINTS) if working > 0 else float('inf')

def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, 'r') as f:
            data = json.load(f)
            return {entry['api_url']: entry for entry in data.get('piped', [])}
    return {}

def save_manifest(instances):
    manifest = {
        "piped": [
            {"name": url.replace("https://", ""), "api_url": url}
            for url, _ in sorted(instances.items(), key=lambda x: x[1]['time'])
        ]
    }
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)

def git_commit_and_push():
    try:
        subprocess.run(["git", "add", MANIFEST_PATH], check=True)
        subprocess.run(["git", "commit", "-m", "update piped_manifest.json"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Manifest-Datei wurde per git gepusht.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Git-Push: {e}")

def add_instance(url, existing):
    if url in existing:
        print(f"🔁 Instanz bereits vorhanden: {url}")
        return
    print(f"🧪 Teste neue Instanz: {url}")
    score, avg_time = test_instance(url)
    if score >= MIN_SCORE:
        print(f"✅ Kompatibel ({score}/4) – {avg_time:.3f}s")
        existing[url] = {"score": score, "time": avg_time}
    else:
        print(f"❌ Nicht kompatibel ({score}/4)")

def main():
    print("\n📦 Lade bestehende Manifest-Datei...")
    instances = load_manifest()

    print("\n🔍 Prüfe vorhandene Instanzen auf aktuelle Erreichbarkeit...")
    updated = {}
    for url in instances:
        print(f"→ {url}")
        score, avg_time = test_instance(url)
        if score >= MIN_SCORE:
            print(f"  ✅ OK ({score}/4) – {avg_time:.3f}s")
            updated[url] = {"score": score, "time": avg_time}
        else:
            print(f"  ⚠️  Entfernt – nur {score}/4 erreichbar")

    print("\n➕ Möchtest du neue Instanzen hinzufügen? Gib sie einzeln ein (https...), ENTER zum Beenden:")
    while True:
        new_url = input("Neue Instanz: ").strip()
        if not new_url:
            break
        add_instance(new_url, updated)

    print("\n💾 Speichere aktualisiertes Manifest...")
    save_manifest(updated)
    print(f"✅ Fertig. Datei gespeichert als: {MANIFEST_PATH}\n")

    print("🚀 Möchtest du das Manifest automatisch committen und pushen? [j/N]")
    if input("> ").lower() == 'j':
        git_commit_and_push()

if __name__ == "__main__":
    main()
