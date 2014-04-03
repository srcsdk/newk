#!/bin/bash
while read url; do
    echo "--- $url ---"
    curl -s "$url" | grep -oP '(?<=<title>).*?(?=</title>)'
done < feeds.txt
