# Universal USB Point Of Sales Thermal Printer Driver

This is a universal*ish* python driver for USB POS thermal printers.
Simply run it and start typing and every newline it will be sent to the printer.
Also supports input from stdin.
Most printers also support [ESP-POS](https://files.support.epson.com/pdf/general/escp2ref.pdf), for which there are special
commands implemented.

#@!START-ESC = start respecting ESC commands, also resets any set parameters
#@!CUT = Cut paper
#@!BOLD1 / #@!BOLD0 = Bold on/off
#@!UNDER1 / #@!UNDER0 = Underline on/off
#@!DOUBLEW / #@!NORMALW = Double / normal width (does not stack with underline nor double height)

Forked from https://github.com/vpatron/usb_receipt_printer

## Resources
- https://mike42.me/blog/what-is-escpos-and-how-do-i-use-it
- https://github.com/mike42/escpos-php
- https://files.support.epson.com/pdf/general/escp2ref.pdf
- https://mike42.me/blog/2014-10-26-setting-up-an-epson-receipt-printer
- https://wes4m.io/posts/epson_rev/
