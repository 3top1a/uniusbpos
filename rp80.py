#!/usr/bin/env python
import usb
import sys
import signal
import codecs

print("Universal USB Point Of Sales Thermal Printer Driver")
print("By Filip Rusz <USR filip DOMAIN rusz TLD space>")

# Assumes device is 0fe6:811e
dev = usb.core.find(idVendor=0x0fe6, idProduct=0x811e)
if dev is None:
    print("Could not find device!")
    sys.exit(1)

# Detach from kernel
needs_reattach = False
if dev.is_kernel_driver_active(0):
    needs_reattach = True
    dev.detach_kernel_driver(0)

dev.set_configuration()

cfg = dev.get_active_configuration()
intf = cfg[(0,0)]

ep = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT)

if ep is None:
    print("Could not get a valid bulk out endpoint!")
    sys.exit(1)

def quit(sig, frame):
    # Free dev to kernel
    dev.reset()
    if needs_reattach:
        dev.attach_kernel_driver(0)
    sys.exit(0)
# Bind so that the device gets freed
signal.signal(signal.SIGINT, quit)

# ESC constants
ESC = b'\x1b'
GS = b'\x1d'
LF = b'\x0a'
CR = b'\x0d'
BEL = b'\x07'
NUL = b'\x00'

def replace_ascii_consts(i: bytes) -> bytes:
    i = i.replace(b'ESC', ESC)
    i = i.replace(b'GS', GS)
    i = i.replace(b'LF', LF)
    i = i.replace(b'CR', CR)
    i = i.replace(b'BEL', BEL)
    i = i.replace(b'NUL', NUL)
    i = i.replace(b'\\ ', b' ')
    i = i.replace(b'#@!BOLD1', ESC + b'E1')
    i = i.replace(b'#@!BOLD0', ESC + b'E0')
    i = i.replace(b'#@!UNDER1', ESC + b'!\x80')
    i = i.replace(b'#@!UNDER0', ESC + b'!\x00')
    i = i.replace(b'#@!DOUBLEW', ESC + b'!\x20')
    i = i.replace(b'#@!NORMALW', ESC + b'!\x00')
    i = i.replace(b'#@!PAPERW80', GS + b'W\x80\x02')
    i = i.replace(b'#@!PAPERW40', GS + b'W\x40\x01')
    i = i.replace(b'#@!BACK', ESC + b'j\x48')

    return i

try:
    esc = False
    bold = False
    while True:
        i = input()

        if i == "#@!START-ESC":
            esc = True
            ep.write(ESC + b'@')
            print("ESC mode enabled!")
            continue
        elif esc and i == "#@!CUT":
            ep.write('\n\n\n') # There is a three line distance between cutter and printing part
            ep.write(GS + b'V\x00')
            ep.write('\n\n\n')
            continue

        # Convert to bytes for easier byte mucking about

        if esc:
            i = replace_ascii_consts(bytes(codecs.decode(i, 'unicode_escape'), 'utf8'))
        else:
            i = bytes(i, 'utf8')

        # encode i
        ep.write(i + b"\n")

except EOFError:
    quit(None, None)

except Exception as e:
    print(f"Exception: {e}")
    quit(None, None)
