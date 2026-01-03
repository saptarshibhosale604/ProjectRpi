

Raspberry Pi 5 supports USB gadget mode via configfs on the official Raspberry Pi OS (Bookworm or later), but requires specific firmware updates and config changes due to the new RP1 chip. Ben Hardill's guide (referenced in recent articles) provides the foundation, adapted here for HID keyboard use instead of Ethernet.[1]

Follow these exact steps on a fresh or updated Raspberry Pi OS on your Pi 5; test with Ethernet first, then swap for HID.

## Update Firmware and OS

Run these commands on the Pi (via SSH or monitor):
```
sudo apt update && sudo apt full-upgrade -y
sudo rpi-update
sudo reboot
```
This pulls Pi 5-specific RP1 USB gadget support; older images lack it.[1]

## Edit Boot Config Files

1. Edit `/boot/config.txt` (now `/boot/firmware/config.txt` on Bookworm):
```
sudo nano /boot/firmware/config.txt
```
Add at the end:
```
dtoverlay=dwc2
```
Save and exit.

[all]
dtoverlay=dwc2

[cm5]
dtoverlay=dwc2,dr_mode=peripheral


2. Edit `/boot/cmdline.txt`:
```
sudo nano /boot/firmware/cmdline.txt
```
Add to the **end of the single line** (with leading space, no newline):
```
modules-load=dwc2,libcomposite
```
Example full line: `console=serial0,115200 console=tty1 root=PARTUUID=... rootfstype=ext4 ... modules-load=dwc2,libcomposite`

3. Add module to `/etc/modules`:
```
echo "libcomposite" | sudo tee -a /etc/modules
```
Reboot:
```
sudo reboot
```

## Create HID Keyboard Gadget Script

Create `/usr/local/bin/usb-hid-keyboard.sh` (Pi 5 path differs slightly from older guides):
```
sudo nano /usr/local/bin/usb-hid-keyboard.sh
```
Paste this HID-specific script (adapted from Hardill's configfs Ethernet example for keyboard):
```bash
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
```
Make executable:
```
sudo chmod +x /usr/local/bin/usb-hid-keyboard.sh
```
This creates `/dev/hidg0` for writing keyboard reports.[2]

## Enable at Boot

Create systemd service:
```
sudo nano /etc/systemd/system/usb-hid.service
```
Paste:
```
[Unit]
Description=USB HID Keyboard Gadget
After=sysfsinit.target systemd-modules-load.service
Wants=sysfsinit.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/usb-hid-keyboard.sh

[Install]
WantedBy=multi-user.target
```
Enable:
```
sudo systemctl daemon-reload
sudo systemctl enable usb-hid.service
sudo reboot
```

## Test Connection

1. Power off Pi 5.
2. Connect **data-capable USB-C cable** from Pi 5 USB-C (power port) to Windows USB port.
3. Power on Pi 5.
4. On Windows: Check Device Manager for "Pi HID Keyboard" under Human Interface Devices.[1]
5. On Pi: `ls /dev/hid*` shows `/dev/hidg0`.
6. Test: `echo -ne '\\x00\\x00\\x04\\x00\\x00\\x00\\x00\\x00' > /dev/hidg0` (types 'A').[2]

Your GPIO matrix code can now write HID reports to `/dev/hidg0` for custom keys.




// Need a HOME ROW MOD LOCK which act as Caps lock,
HOME ROW MOD LOCK (OFF): when pressed the home row will NOT be have home row mod
HOME ROW MOD LOCK (ON): when pressed the home row will be have home row mod

//  keyboardKeysMetrix5x4HomeModLayer.py, working
keyboard metrix 5x4
Home mod layer

// keyboardArrowKeysMetrix5x4.py
working as expected

// Raspberry pi 5 pin diagram  

| GPIO Pin # | Pin # || Pin # | GPIO Pin # |
|------------|--------||--------|-------------|
|     -      |   1    ||   2    |     -       |
|     2      |   3    ||   4    |     -       |
|     3      |   5    ||   6    |     -       |
|     4      |   7    ||   8    |     14      |
|     -      |   9    ||  10    |     15      |
|    17      |  11    ||  12    |     18      |
|    27      |  13    ||  14    |     -       |
|    22      |  15    ||  16    |     23      |
|     -      |  17    ||  18    |     24      |
|    10      |  19    ||  20    |     -       |
|     9      |  21    ||  22    |     25      |
|    11      |  23    ||  24    |     8       |
|     -      |  25    ||  26    |     7       |
|     0      |  27    ||  28    |     1       |
|     5      |  29    ||  30    |     -       |
|     6      |  31    ||  32    |     12      |
|    13      |  33    ||  34    |     -       |
|    19      |  35    ||  36    |     16      |
|    26      |  37    ||  38    |     20      |
|     -      |  39    ||  40    |     21      |
