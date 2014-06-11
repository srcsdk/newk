#!/bin/bash
while read url; do
    echo ""
    echo "=== $url ==="
    echo ""
    curl -s "$url" | grep -oP '(?<=<title>).*?(?=</title>)' | head -10
    echo ""
done < feeds.txt
