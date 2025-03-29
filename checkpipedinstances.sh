#!/bin/bash

INSTANCES=(
  "https://pipedapi.kavin.rocks"
  "https://pipedapi.tokhmi.xyz"
  "https://pipedapi.moomoo.me"
  "https://pipedapi.syncpundit.io"
  "https://pipedapi.mha.fi"
  "https://piped-api.garudalinux.org"
  "https://pipedapi.rivo.lol"
  "https://pipedapi.leptons.xyz"
  "https://piped-api.lunar.icu"
  "https://pipedapi.colinslegacy.com"
  "https://pipedapi.orangenet.cc"
)

ENDPOINTS=(
  "/api/v1/search?q=test"
  "/api/v1/streams/abc123"
  "/api/v1/channels/UC_x5XG1OV2P6uZZ5FSM9Ttw"
  "/api/v1/suggestions?q=test"
)

echo "-------------------------------------------------------------"
echo "📡 Yattee-Kompatibilitätscheck für Piped-API-Instanzen"
echo "-------------------------------------------------------------"

for URL in "${INSTANCES[@]}"; do
  echo ""
  echo "🔍 Prüfe $URL"
  SCORE=0
  for EP in "${ENDPOINTS[@]}"; do
    FULL="$URL$EP"
    RESULT=$(curl -A "Yattee" -s -o /dev/null -w "%{http_code} %{time_total}" "$FULL")
    STATUS=$(echo "$RESULT" | cut -d' ' -f1)
    TIME=$(echo "$RESULT" | cut -d' ' -f2)

    if [[ "$STATUS" == "200" || "$STATUS" == "400" || "$STATUS" == "404" ]]; then
      echo "  [✓] $EP  (HTTP $STATUS) in ${TIME}s"
      ((SCORE++))
    else
      echo "  [✗] $EP  (HTTP $STATUS) in ${TIME}s"
    fi
  done

  if [ "$SCORE" -ge 3 ]; then
    echo "✅ Kompatibel ($SCORE/4 erfolgreich)"
  else
    echo "❌ Nicht kompatibel ($SCORE/4)"
  fi
done

