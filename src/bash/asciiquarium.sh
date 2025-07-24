#!/bin/bash


API_URL="http://localhost:5001/trigger_event"


if [[ "$1" == "start" ]]; then
	curl -X POST "$API_URL" \
	    -H "Content-Type: application/json" \
	    -d '{"event_type":"asciiquarium_streamstart","event_data":{"user":"'"$USER"'","timestamp":"'"$(date -Iseconds)"'"}}'

elif [[ -z "$1" ]]; then
	curl -X POST "$API_URL" \
	    -H "Content-Type: application/json" \
	    -d '{"event_type":"asciiquarium_start","event_data":{"user":"'"$USER"'","timestamp":"'"$(date -Iseconds)"'"}}'

else
	exit 1
fi

asciiquarium

curl -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"event_type":"asciiquarium_end","event_data":{"user":"'"$USER"'","timestamp":"'"$(date -Iseconds)"'"}}'
