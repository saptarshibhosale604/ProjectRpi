#!/bin/bash

# PySpark installation script for Raspberry Pi 5 (Debian 12 bookworm aarch64)
# Optimized for 8GB RAM system with ~28GB storage [memory:5]

set -e  # Exit on error

echo "=== Updating Debian packages ==="
sudo apt update && sudo apt upgrade -y

echo "=== Installing Java 17 (OpenJDK) for PySpark 4.x ==="
# sudo apt install -y openjdk-17-jdk python3 python3-pip python3-venv curl [web:43][web:26]
sudo apt install -y openjdk-17-jdk python3 python3-pip python3-venv curl 

echo "=== Setting JAVA_HOME for current session ==="
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64  # Standard Debian 12 aarch64 path [web:26]

echo "=== Verifying Java installation ==="
java -version
echo "JAVA_HOME: $JAVA_HOME"

echo "=== Installing PySpark 4.0.1 via pip ==="
# pip3 install --user --no-cache-dir pyspark==4.0.1
pip3 install --user pyspark==4.0.1 --break-system-packages

echo "=== Setting up permanent environment variables ==="
mkdir -p ~/.local/share/pyspark
mkdir -p ~/.bashrc.d/
cat > ~/.bashrc.d/pyspark.sh << 'EOF'
# PySpark environment for Raspberry Pi 5
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
export PATH="$JAVA_HOME/bin:$PATH"
export PYSPARK_PYTHON=python3
export SPARK_LOCAL_IP="127.0.0.1"
EOF

echo "=== Sourcing environment (current session) ==="
source ~/.bashrc.d/pyspark.sh

echo "=== Testing PySpark installation ==="
python3 -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('rpi-test').master('local[*]').getOrCreate()
df = spark.range(5).toDF('number')
print('✅ PySpark working on Raspberry Pi 5!')
df.show()
spark.stop()
print('Test PASSED!')
" [memory:1]

echo "=== Installation complete! ==="
echo "1. Run: source ~/.bashrc.d/pyspark.sh  (or restart terminal)"
echo "2. Test with: pyspark"
echo "3. Memory optimized for your 8GB RPi5 - uses local[*] mode [memory:5]"
echo ""
echo "Usage example:"
echo "pyspark"
echo "-- or --"
echo "python3 -c \"import pyspark; print('PySpark', pyspark.__version__)\""

echo "=== Save as install_pyspark_rpi5.sh and run: ==="
echo "chmod +x install_pyspark_rpi5.sh && ./install_pyspark_rpi5.sh [memory:3]"


