#!/bin/bash

echo "=============================="
echo " Raspberry Pi 5 Performance"
echo "=============================="
echo

# CPU info
echo "🧠 CPU Info"
lscpu | grep -E 'Model name|CPU MHz|CPU max MHz|CPU min MHz'
echo

# CPU temperature
echo "🌡️ CPU Temperature"
vcgencmd measure_temp 2>/dev/null || echo "vcgencmd not available"
echo

# CPU frequency
echo "⚡ CPU Frequency"
vcgencmd measure_clock arm 2>/dev/null || echo "vcgencmd not available"
echo

# Throttling status
echo "🚨 Throttling Status"
vcgencmd get_throttled 2>/dev/null || echo "vcgencmd not available"
echo

# Memory usage
echo "💾 Memory Usage"
free -h
echo

# GPU memory split
echo "🎮 GPU Memory"
vcgencmd get_mem gpu 2>/dev/null || echo "vcgencmd not available"
echo

# Disk usage
echo "📀 Disk Usage"
df -h /
echo

# Load average
echo "📊 Load Average"
uptime
echo

# Voltage info (important for Pi 5 stability)
echo "🔌 Voltage"
vcgencmd measure_volts core 2>/dev/null || echo "vcgencmd not available"
echo

echo "=============================="
echo " End of Performance Report"
echo "=============================="

