#!/bin/bash

# Check if pattern name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <pattern_name>"
  exit 1
fi

PATTERN_NAME=$1
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# from rasbperry pi
# INPUT_FILE="/home/ssbrpi/Project/Fabric/Data/input.txt"
# HELP_FILE="/home/ssbrpi/Project/Fabric/Data/fabricPatternHelp.md"
# OUTPUT_FILE="/home/ssbrpi/Project/Fabric/Data/${TIMESTAMP}-${PATTERN_NAME}.md"

# From docker Personal Assistant
INPUT_FILE="/root/Project/Fabric/Data/input.txt"
HELP_FILE="/root/Project/Fabric/Data/fabricPatternHelp.md"
OUTPUT_FILE="/root/Project/Fabric/Data/${TIMESTAMP}-${PATTERN_NAME}.md"

if [ "$PATTERN_NAME" == "help" ]; then
  cat "$HELP_FILE"
else
  cat "$INPUT_FILE" | /home/ssbrpi/Project/Fabric/fabric -sp "$PATTERN_NAME" | tee "$OUTPUT_FILE"
fi
