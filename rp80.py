#!/usr/bin/env python
import usb
import sys
import signal

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

    return i

# Commands for fuzzing
FUZZCMD = [
    b'\x07',  # BEL Beeper
    b'\x08',  # BS Backspace
    b'\x09',  # HT Tab horizontally
    b'\x0a',  # LF Line feed
    b'\x0b',  # VT Tab vertically
    b'\x0c',  # FF Form feed
    b'\x0d',  # CR Carriage return
    b'\x0e',  # SO Select double-width printing (one line)
    b'\x0f',  # SI Select condensed printing
    b'\x11',  # DC1 Select printer
    b'\x12',  # DC2 Cancel condensed printing
    b'\x13',  # DC3 Deselect printer
    b'\x14',  # DC4 Cancel double-width printing (one line)
    b'\x18',  # CAN Cancel line
    b'\x1b\x0e',  # ESC SO Select double-width printing (one line)
    b'\x1b\x0f',  # ESC SI Select condensed printing
    b'\x1b\x19',  # ESC EM Control paper loading/ejecting
    b'\x1b\x20',  # ESC SP Set intercharacter space
    b'\x1b\x21',  # ESC ! Master select
    b'\x1b\x23',  # ESC # Cancel MSB control
    b'\x1b\x24',  # ESC $ Set absolute horizontal print position
    b'\x1b\x25',  # ESC % Select user-defined set
    b'\x1b\x26',  # ESC & Define user-defined characters
    b'\x1b\x28\x2d',  # ESC ( - Select line/score
    b'\x1b\x28\x42',  # ESC ( B Bar code setup and print
    b'\x1b\x28\x43',  # ESC ( C Set page length in defined unit
    b'\x1b\x28\x47',  # ESC ( G Select graphics mode
    b'\x1b\x28\x55',  # ESC ( U Set unit
    b'\x1b\x28\x56',  # ESC ( V Set absolute vertical print position
    b'\x1b\x28\x5e',  # ESC ( ^ Print data as characters
    b'\x1b\x28\x63',  # ESC ( c Set page format
    b'\x1b\x28\x69',  # ESC ( i Select MicroWeave print mode
    b'\x1b\x28\x74',  # ESC ( t Assign character table
    b'\x1b\x28\x76',  # ESC ( v Set relative vertical print position
    b'\x1b\x2a',  # ESC * Select bit image
    b'\x1b\x2b',  # ESC + Set n/360-inch line spacing
    b'\x1b\x2d',  # ESC - Turn underline on/off
    b'\x1b\x2e',  # ESC . Print raster graphics
    b'\x1b\x2e\x32',  # ESC . 2 Enter TIFF compressed mode
    b'\x1b\x2f',  # ESC / Select vertical tab channel
    b'\x1b\x30',  # ESC 0 Select 1/8-inch line spacing
    b'\x1b\x31',  # ESC 1 Select 7/72-inch line spacing
    b'\x1b\x32',  # ESC 2 Select 1/6-inch line spacing
    b'\x1b\x33',  # ESC 3 Set n/180-inch line spacing
    b'\x1b\x33\x32',  # ESC 3 Set n/216-inch line spacing
    b'\x1b\x34',  # ESC 4 Select italic font
    b'\x1b\x35',  # ESC 5 Cancel italic font
    b'\x1b\x36',  # ESC 6 Enable printing of upper control codes
    b'\x1b\x37',  # ESC 7 Enable upper control codes
    b'\x1b\x38',  # ESC 8 Disable paper-out detector
    b'\x1b\x39',  # ESC 9 Enable paper-out detector
    b'\x1b\x3a',  # ESC : Copy ROM to RAM
    b'\x1b\x3c',  # ESC < Unidirectional mode (one line)
    b'\x1b\x3d',  # ESC = Set MSB to 0
    b'\x1b\x3e',  # ESC > Set MSB to 1
    b'\x1b\x3f',  # ESC ? Reassign bit-image mode
    b'\x1b\x40',  # ESC @ Initialize printer
    b'\x1b\x41',  # ESC A Set n/60-inch line spacing
    b'\x1b\x41\x32',  # ESC A Set n/72-inch line spacing
    b'\x1b\x42',  # ESC B Set vertical tabs
    b'\x1b\x43',  # ESC C Set page length in lines
    b'\x1b\x43\x00',  # ESC C NUL Set page length in inches
    b'\x1b\x44',  # ESC D Set horizontal tabs
    b'\x1b\x45',  # ESC E Select bold font
    b'\x1b\x46',  # ESC F Cancel bold font
    b'\x1b\x47',  # ESC G Select double-strike printing
    b'\x1b\x48',  # ESC H Cancel double-strike printing
    b'\x1b\x49',  # ESC I Enable printing of control codes
    b'\x1b\x4a',  # ESC J Advance print position vertically
    b'\x1b\x4b',  # ESC K Select 60-dpi graphics
    b'\x1b\x4c',  # ESC L Select 120-dpi graphics
    b'\x1b\x4d',  # ESC M Select 10.5-point, 12-cpi
    b'\x1b\x4d\x32',  # ESC M Select 12-cpi
    b'\x1b\x4e',  # ESC N Set bottom margin
    b'\x1b\x4f',  # ESC O Cancel bottom margin
    b'\x1b\x50',  # ESC P Select 10.5-point, 10-cpi
    b'\x1b\x50\x32',  # ESC P Select 10-cpi
    b'\x1b\x51',  # ESC Q Set right margin
    b'\x1b\x52',  # ESC R Select an international character set
    b'\x1b\x53',  # ESC S Select superscript/subscript printing
    b'\x1b\x54',  # ESC T Cancel superscript/subscript printing
    b'\x1b\x55',  # ESC U Turn unidirectional mode on/off
    b'\x1b\x57',  # ESC W Turn double-width printing on/off
    b'\x1b\x58',  # ESC X Select font by pitch and point
    b'\x1b\x59',  # ESC Y Select 120-dpi, double-speed graphics
    b'\x1b\x5a',  # ESC Z Select 240-dpi graphics
    b'\x1b\x5c',  # ESC \ Set relative horizontal print position
    b'\x1b\x5e',  # ESC ^ Select 60/120-dpi, 9-pin graphics
    b'\x1b\x61',  # ESC a Select justification
    b'\x1b\x62',  # ESC b Set vertical tabs in VFU channels
    b'\x1b\x63',  # ESC c Set horizontal motion index (HMI)
    b'\x1b\x65',  # ESC e Set fixed tab increment
    b'\x1b\x66',  # ESC f Horizontal/vertical skip
    b'\x1b\x67',  # ESC g Select 10.5-point, 15-cpi
    b'\x1b\x67\x32',  # ESC g Select 15-cpi
    b'\x1b\x69',  # ESC i Select immediate print mode
    b'\x1b\x6a',  # ESC j Reverse paper feed
    b'\x1b\x6b',  # ESC k Select typeface
    b'\x1b\x6c',  # ESC l Set left margin
    b'\x1b\x6d',  # ESC m Select printing of upper control codes
    b'\x1b\x70',  # ESC p Turn proportional mode on/off
    b'\x1b\x71',  # ESC q Select character style
    b'\x1b\x72',  # ESC r Select printing color
    b'\x1b\x73',  # ESC s Select low-speed mode
    b'\x1b\x74',  # ESC t Select character table
]

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
        elif esc and i == "#@!FUZZ":
            ep.write("\x1b\x2a\x00\x01\x60\x01\x1f\x01\x00\x08\x00\x01\x00\x01\x00")

        # Convert to bytes for easier byte mucking about
        i = bytes(i, 'utf8')

        if esc:
            i = replace_ascii_consts(i)

        # encode i
        ep.write(i + b"\n")

except EOFError:
    quit(None, None)

except Exception as e:
    print(f"Exception: {e}")
    quit(None, None)
