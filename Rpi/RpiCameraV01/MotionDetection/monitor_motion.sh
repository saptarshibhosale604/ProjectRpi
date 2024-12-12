LOG_FILE="motion_log.txt"

# Monitor the log file for motion detection keyword
tail -F "motion_log.txt" | while read -r line; do
    # Adjust this condition to match your motion detection log
    if echo "$line" | grep -q "Motion detected"; then
        echo "Motion detected!"
        ./task.sh
    fi
done
