#!/bin/bash
set -e

G=/sys/kernel/config/usb_gadget/pi_keyboard

[ -e $G/UDC ] && echo "" > $G/UDC
rm -f $G/configs/c.1/hid.usb0
rmdir $G/functions/hid.usb0
rmdir $G/configs/c.1/strings/0x409
rmdir $G/configs/c.1
rmdir $G/strings/0x409
rmdir $G

