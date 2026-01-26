#!/bin/bash
# Test script to verify ffmpeg is working

set -e

echo "=== Testing ffmpeg installation ==="
echo "1. Checking ffmpeg binary..."
if [ -f /usr/local/bin/ffmpeg ]; then
    echo "✅ ffmpeg binary found at /usr/local/bin/ffmpeg"
    ls -la /usr/local/bin/ffmpeg
else
    echo "❌ ffmpeg binary not found!"
    exit 1
fi

echo ""
echo "2. Testing ffmpeg execution..."
if /usr/local/bin/ffmpeg -version 2>&1 | head -3; then
    echo "✅ ffmpeg runs successfully"
else
    echo "❌ ffmpeg failed to execute"
    ldd /usr/local/bin/ffmpeg 2>&1 || echo "Could not run ldd"
    exit 1
fi

echo ""
echo "3. Checking library dependencies..."
echo "Required libraries:"
ldd /usr/local/bin/ffmpeg | grep -E "not found|=>|linux-vdso" || true

echo ""
echo "=== All ffmpeg tests passed! ==="
