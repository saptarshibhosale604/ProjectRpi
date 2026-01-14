#!/bin/bash
modprobe libcomposite

cd /sys/kernel/config/usb_gadget/
mkdir -p pi_keyboard
cd pi_keyboard

# USB identifiers (standard for HID keyboard compatibility with Windows)
echo 0x1d6b > idVendor  # Linux Foundation
echo 0x0104 > idProduct # HID Keyboard
echo 0x0100 > bcdDevice # v1.0.0
echo 0x0200 > bcdUSB    # USB 2.0

mkdir -p strings/0x409
echo "fedcba9876543210" > strings/0x409/serialnumber
echo "Raspberry Pi"     > strings/0x409/manufacturer
echo "Pi HID Keyboard"  > strings/0x409/product

mkdir -p configs/c.1/strings/0x409
echo "HID Config"     > configs/c.1/strings/0x409/configuration
echo 500              > configs/c.1/MaxPower
echo 0xa0             > configs/c.1/bmAttributes # Self-powered, remote wakeup

# HID function for keyboard (report descriptor for boot keyboard)
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol    # Keyboard
echo 1 > functions/hid.usb0/subclass    # Boot interface
echo 3 > functions/hid.usb0/report_length

# Standard USB HID keyboard report descriptor (8 bytes: modifiers, reserved, 6 keys)
echo -ne \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0 > functions/hid.usb0/report_desc

ln -s functions/hid.usb0 configs/c.1/

udevadm settle
ls /sys/class/udc > UDC  # Bind to Pi 5 UDC (e.g., dwc2 or rp1_udc)

