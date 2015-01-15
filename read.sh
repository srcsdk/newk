#!/bin/bash
if [ ! -f feeds.txt ]; then
    echo "feeds.txt not found"
    exit 1
fi

while read -r url; do
    [ -z "$url" ] && continue
    echo ""
    echo "[$url]"
    result=$(curl -s --max-time 10 "$url" 2>/dev/null | grep -oP '(?<=<title>).*?(?=</title>)' | head -10)
    if [ -z "$result" ]; then
        echo "  (no results)"
    else
        echo "$result" | while read -r line; do
            echo "  $line"
        done
    fi
done < feeds.txt
