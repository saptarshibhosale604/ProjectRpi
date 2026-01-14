#!/bin/bash
set -e

G=/sys/kernel/config/usb_gadget/keyboard

mkdir -p $G
echo 0x1d6b > $G/idVendor
echo 0x0104 > $G/idProduct
echo 0x0100 > $G/bcdDevice
echo 0x0200 > $G/bcdUSB

mkdir -p $G/strings/0x409
echo "SSB Automation" > $G/strings/0x409/manufacturer
echo "Custom Keyboard" > $G/strings/0x409/product
echo "0001" > $G/strings/0x409/serialnumber

mkdir -p $G/configs/c.1
mkdir -p $G/configs/c.1/strings/0x409
echo "Keyboard + Media" > $G/configs/c.1/strings/0x409/configuration
echo 250 > $G/configs/c.1/MaxPower

# ---------- Keyboard HID ----------
mkdir -p $G/functions/hid.usb0
echo 1 > $G/functions/hid.usb0/protocol
echo 1 > $G/functions/hid.usb0/subclass
echo 8 > $G/functions/hid.usb0/report_length

echo -ne \
'\x05\x01\x09\x06\xa1\x01\x05\x07\x19\xe0\x29\xe7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\
\x95\x01\x75\x08\x81\x01\x95\x06\x75\x08\x15\x00\x25\x65\x05\x07\x19\x00\x29\x65\x81\x00\xc0' \
> $G/functions/hid.usb0/report_desc

# ---------- Consumer HID ----------
mkdir -p $G/functions/hid.usb1
echo 0 > $G/functions/hid.usb1/protocol
echo 0 > $G/functions/hid.usb1/subclass
echo 2 > $G/functions/hid.usb1/report_length

echo -ne \
'\x05\x0c\x09\x01\xa1\x01\x15\x00\x26\xff\x03\x19\x00\x2a\xff\x03\x75\x10\x95\x01\x81\x00\xc0' \
> $G/functions/hid.usb1/report_desc

ln -s $G/functions/hid.usb0 $G/configs/c.1/
ln -s $G/functions/hid.usb1 $G/configs/c.1/

ls /sys/class/udc > $G/UDC
