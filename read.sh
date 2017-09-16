#!/bin/bash
if [ ! -f feeds.txt ]; then
    echo "feeds.txt not found"
    exit 1
fi

echo "$(date '+%Y-%m-%d %H:%M')"
echo ""

while read -r url; do
    [ -z "$url" ] && continue
    echo "[$url]"
    result=$(curl -s --max-time 10 "$url" 2>/dev/null | grep -oP '(?<=<title>).*?(?=</title>)' | tail -n +2 | head -5)
    if [ -z "$result" ]; then
        echo "  (unreachable)"
    else
        echo "$result" | while read -r line; do
            echo "  - $line"
        done
    fi
    echo ""
done < feeds.txt
