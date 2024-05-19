#!/usr/bin/env python
import usb
import sys
import signal
import codecs
from typing import Optional

print("Universal USB Point Of Sales Thermal Printer Driver")
print("By Filip Rusz <USR filip DOMAIN rusz TLD space>")

def find_device_by_id(idVendor: int, idProduct: int) -> usb.core.Device:
    dev = usb.core.find(idVendor=idVendor, idProduct=idProduct)
    assert dev is not None, "Could not find device!"
    return dev

def configure_device_get_endpoint(dev: usb.core.Device) -> usb.core.Endpoint:
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
    dev.set_configuration()
    cfg = dev.get_active_configuration()
    intf = cfg[(0, 0)]
    ep = usb.util.find_descriptor(
        intf,
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
    )
    assert ep is not None, "Could not get a valid bulk out endpoint!"
    return ep

def quit_program(sig, frame, dev: usb.core.Device) -> None:
    dev.reset()
    if dev.is_kernel_driver_active(0):
        dev.attach_kernel_driver(0)
    sys.exit(0)

def replace_ascii_consts(data: bytes) -> bytes:
    replacements = {
        b'ESC': b'\x1b',
        b'GS': b'\x1d',
        b'LF': b'\x0a',
        b'CR': b'\x0d',
        b'BEL': b'\x07',
        b'NUL': b'\x00',
        b'#@!BOLD1': b'\x1bE1',
        b'#@!BOLD0': b'\x1bE0',
        b'#@!UNDER1': b'\x1b!\x80',
        b'#@!UNDER0': b'\x1b!\x00',
        b'#@!DOUBLEW': b'\x1b!\x20',
        b'#@!NORMALW': b'\x1b!\x00',
        b'#@!PAPERW80': b'\x1dW\x80\x02',
        b'#@!PAPERW40': b'\x1dW\x40\x01',
        b'#@!BACK': b'\x1bj\x48',
        b'#@!CUT': b'\n\n\n\x1dV\x00\n\n\n' # There is a three line distance between cutter and printing part
    }
    for k, v in replacements.items():
        data = data.replace(k, v)
    return data

def process_input(ep: usb.core.Endpoint, dev: usb.core.Device) -> None:
    esc = False
    try:
        while True:
            i = input()
            if i == "#@!START-ESC":
                esc = True
                ep.write(b'\x1b@')
                print("ESC mode enabled!")
                continue

            if esc:
                i = replace_ascii_consts(bytes(codecs.decode(i, 'unicode_escape'), 'utf8'))
            else:
                i = bytes(i, 'utf8')

            ep.write(i + b"\n")

    except EOFError:
        quit_program(None, None, dev)
    except Exception as e:
        print(f"Exception: {e}")
        quit_program(None, None, dev)

if __name__ == "__main__":
    # Main execution
    dev = find_device_by_id(idVendor=0x0fe6, idProduct=0x811e)
    ep = configure_device_get_endpoint(dev)
    signal.signal(signal.SIGINT, lambda sig, frame: quit_program(sig, frame, dev))
    process_input(ep, dev)
    quit_program(None, None, dev)
