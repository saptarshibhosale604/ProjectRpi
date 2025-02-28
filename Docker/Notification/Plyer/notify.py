#!/usr/bin/env python3
from plyer import notification
import sys

def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name='CustomReminder',
        timeout=10  # duration in seconds
    )

if __name__ == '__main__':
    # Use default title and message if not provided via command-line arguments
    title = sys.argv[1] if len(sys.argv) > 1 else "Reminder"
    message = sys.argv[2] if len(sys.argv) > 2 else "This is your custom reminder notification!"
    
    send_notification(title, message)
