# Flashing bootloader on to Ender 3

1. https://letsprint3d.net/guide-how-to-flash-a-bootloader-on-melzi-boards/
2. If you see an error like `avrdude: stk500_getsync() attempt 1 of 10: not in sync: resp=0x15`, then you likely need a ≥ 10µF capacitor between the Arduino's `Reset` and `GND` pins.