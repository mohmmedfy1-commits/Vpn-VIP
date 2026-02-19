#!/bin/bash

echo "Downloading Xray Android arm64..."

wget -O xray.zip https://github.com/XTLS/Xray-core/releases/latest/download/Xray-android-arm64-v8a.zip

unzip -o xray.zip

chmod +x xray

echo "Xray Android installed successfully"
