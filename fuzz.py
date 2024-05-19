from rp80 import *
import time

dev = find_device_by_id(idVendor=0x0fe6, idProduct=0x811e)
ep = configure_device_get_endpoint(dev)
signal.signal(signal.SIGINT, lambda sig, frame: quit_program(sig, frame, dev))

ep.write(b'\x1B\x40') # init

sequences = [
    b'\x1B\x40',  # Initialize printer
    b'\x1D\x56\x00',  # Cut paper (partial)
    b'\x1D\x56\x01',  # Cut paper (feed and cut)
    b'\x1D\x56\x41',  # Cut paper (partial with paper feed)
    b'\x1B\x33\x00',  # Set line spacing to minimum
    b'\x1B\x33\xFF',  # Set line spacing to maximum
    b'\x1B\x32',  # Set default line spacing
    b'\x1B\x4D\x00',  # Select 9x17 font (Font A)
    b'\x1B\x4D\x01',  # Select 12x24 font (Font B)
    b'\x1B\x45\x00',  # Turn off bold mode
    b'\x1B\x45\x01',  # Turn on bold mode
    b'\x1B\x2D\x00',  # Turn off underline mode
    b'\x1B\x2D\x01',  # Turn on underline mode (1-dot thick)
    b'\x1B\x2D\x02',  # Turn on underline mode (2-dots thick)
    b'\x1B\x34',  # Turn on double height mode
    b'\x1B\x35',  # Turn off double height mode
    b'\x1D\x21\x00',  # Select character size normal
    b'\x1D\x21\x11',  # Select character size double width and height
    b'\x1B\x61\x00',  # Left justify
    b'\x1B\x61\x01',  # Center justify
    b'\x1B\x61\x02',  # Right justify
    b'\x1B\x42\x00',  # Turn off black/white reverse print mode
    b'\x1B\x42\x01',  # Turn on black/white reverse print mode
    b'\x1D\x42\x00',  # Turn off white/black reverse print mode
    b'\x1D\x42\x01',  # Turn on white/black reverse print mode
    b'\x1B\x70\x00\x20\x20',  # Generate pulse at Real-Time Clock peripheral device (connector pin 2)
    b'\x1B\x70\x01\x20\x20',  # Generate pulse at Real-Time Clock peripheral device (connector pin 5)
    b'\x1B\x56\x00',  # Select paper cut mode and cut paper (partial cut)
    b'\x1B\x56\x01',  # Select paper cut mode and cut paper (full cut)
    b'\x1B\x44\x10\x14\x1C\x00',  # Set tab positions
    b'\x1B\x50\x00\x05',  # Turn page mode print direction to the right
    # Add graphics commands
    b'\x1D\x76\x30\x00\x10\x10\x01\x00\x00\x00\x00\x00',  # Print raster bit image
    b'\x1B\x2A\x21\x30\x30',  # Print graphics
    # QR Code commands
    b'\x1D\x28\x6B\x03\x00\x31\x43\x03',  # Select the model of QR Code
    b'\x1D\x28\x6B\x03\x00\x31\x45\x30',  # Set QR Code error correction level
    b'\x1D\x28\x6B\x07\x00\x31\x50\x30Hello!',  # Store QR Code data
    b'\x1D\x28\x6B\x03\x00\x31\x51\x30',  # Print QR Code
    # Beep sound generation
    b'\x1B\x1E',  # Generate beep sound
    # Barcode commands
    b'\x1D\x6B\x04\x20\x20\x20\x20\x20\x00',  # Print barcode
    b'\x1B\x74\x00',  # Select character code table (page 0 - PC437: USA, Standard Europe)
    b'\x1B\x74\x01',  # Select character code table (page 1 - Katakana)
    b'\x1B\x74\x02',  # Select character code table (page 2 - Multilingual (Latin I) 
    b'\x1B\x74\x03',  # Select character code table (page 3 - Russian (Cyrillic 2))
    b'\x1B\x6B\x01',  # Print 45-degree right-hand white/black reverse inclined characters
    b'\x1B\x6B\x00',  # Cancel 45-degree right-hand white/black reverse inclined characters
    b'\x1B\x7B\x00',  # Cancel upside-down printing mode
    b'\x1B\x7B\x01',  # Enable upside-down printing mode
    b'\x1B\x2B\x41',  # Print one diode matrix in double high/wide printing mode
    b'\x1D\x77\x02',  # Set barcode width 2 dots
    b'\x1D\x77\x03',  # Set barcode width 3 dots
    b'\x1D\x77\x04',  # Set barcode width 4 dots
    b'\x1D\x48\x00',  # Print HRI (Human Readable Interpretation) characters, not below bar code
    b'\x1D\x48\x01',  # Print HRI characters below bar code
    b'\x1D\x79\x00',  # Print CODABAR barcode
    b'\x1D\x6B\x41\x0c1234567890123',  # Print UPC-A barcode
    b'\x1D\x6B\x42\x0c123456789012',  # Print UPC-E barcode
    b'\x1D\x6B\x43\x0d12345678901234',  # Print EAN13 barcode
    b'\x1D\x6B\x44\x0812345678',  # Print EAN8 barcode
    b'\x1D\x6B\x45\x0aCODE39',  # Print CODE39 barcode
    b'\x1D\x6B\x49\x07INTER2OF5',  # Print Interleaved 2 of 5 barcode
    b'\x1D\x66\x00',  # Disable PDF417 symbol printing mode
    b'\x1D\x66\x01',  # Enable PDF417 symbol printing mode
    b'\x1D\x4C\x01',  # Set paper layout in standard format
    b'\x1D\x4C\x02',  # Set paper layout in Japanese Industrial Standards (JIS) format
    b'\x1D\x4C\x03',  # Set paper layout in International Organization for Standardization (ISO) format
    b'\x1B\x28\x44\x05\x00\x01\x00\x64\x00',  # Print and feed paper to cut mark

    b'\x1E\x4F\x00',  # Disable smoothing mode
    b'\x1E\x4F\x01',  # Enable smoothing mode
    b'\x10\x14\x01\x00\x02',  # Print "Data is passed" response within the status transmission
    b'\x10\x12\x01',  # Transmit printer status
    b'\x10\x23\x04',  # Transmit panel switch status
    b'\x1B\x63\x35\x00',  # Disable panel buttons
    b'\x1B\x63\x35\x01',  # Enable panel buttons
    b'\x1D\x61\x01',  # Enable Automatic Status Back (ASB)
    b'\x1D\x61\x00',  # Disable Automatic Status Back (ASB)
    b'\x1D\x49\x00',  # Query printer status byte 1 and printer identification
    b'\x1D\x49\x01',  # Query printer status byte 2 and printer identification
    
    b'\x1B\x57\x01',  # Turn white/black reverse print mode on
    b'\x1B\x57\x00',  # Turn white/black reverse print mode off
    b'\x1B\x64\x05',  # Feed paper by 5 lines
    b'\x1B\x6C\x00',  # Select page mode
    b'\x1B\x6C\x01',  # Select standard mode
    b'\x1D\x56\x42',  # Perform full cut
    b'\x1B\x75\x01',  # Adjust vertical print position by increment (1 dot line)
    b'\x1B\x75\xFF',  # Adjust vertical print position by decrement (-1 dot line)
    b'\x1B\x64\x00',  # Print and feed paper by 1 line
    b'\x1B\x64\x0A',  # Print and feed paper by 10 lines
    b'\x1B\x64\xFF',  # Paper feed reverse
    b'\x1B\x6A\x00',  # Execute unidirectional printing for mini-line thermal printer
    b'\x1B\x6A\x01',  # Execute bidirectional printing for high-speed thermal printer

    b'\x1B\x2D\x00',  # Cancel underline printing
    b'\x1B\x2D\x01',  # Set underline printing at 1-dot width
    b'\x1B\x2D\x02',  # Set underline printing at 2-dot width

    b'\x1D\x79\x0C',  # Print CODE128 barcode
    b'\x1D\x79\x48',  # Print GS1-128 barcode
    b'\x1D\x79\x64',  # Print GS1 DataBar barcode
    b'\x1D\x79\x70',  # Print GS1 DataBar Expanded barcode

    b'\x1B\x45\x01',  # Enable emphasized printing mode
    b'\x1B\x45\x00',  # Disable emphasized printing mode
    b'\x1B\x47\x01',  # Double printing enabled
    b'\x1B\x47\x00',  # Double printing disabled

    b'\x1D\x76\x30\x02\x00\x10\x00\x00',  # Bit raster graphics mode with scaling factor (bit 0 cleared or set)
    
    b'\x1B\x25\x01',  # Select user character set
    b'\x1B\x25\x00',  # Select default character set
    b'\x1B\x25\x01',  # Start defining user-defined characters
    b'\x1B\x26',      # Define user-defined characters

    b'\x1B\x3D\x01',  # Select peripheral device at connector pin 2
    b'\x1B\x3D\x02',  # Select peripheral device at connector pin 5

    b'\x1C\x26',      # Select Kanji character mode
    b'\x1C\x2E',      # Cancel Kanji character mode
    b'\x1C\x21\x00',  # Specify double-byte character code parsing mode (Kanji JIS charset)
    b'\x1C\x57\x01',  # Kanji double width and height mode enable
    b'\x1C\x57\x00',  # Kanji double width and height mode disable

    b'\x1F\x11',      # Enter non-historical data vent mode
    b'\x1F\x12',      # Enter historical data vent mode

    b'\x1F\x43\x00',  # Select character "A"
    b'\x1F\x43\x01',  # Select character "B"
    b'\x1B\x56\x00',  # Enter printer control mode
    b'\x1B\x56\x01',  # Exit printer control mode

    b'\x1B\x27\x12',  # Configure mini dots per ejection (20)
    b'\x1B\x27\x14',  # Configure mini dots per ejection (20)
    
    b'\x1B\x41\x00',  # Repeat printing off (non-volatile)
    b'\x1B\x56\x00',  # Enter maintenance mode
    b'\x1B\x3B\x01',  # Options on
    b'\x1B\x3B\x00',  # Options off

    b'\x1D\x4E\x55',  # End barcode printing in certain modes
    b'\x1D\x4E\x53',  # Start barcode printing in certain modes
    
    b'\x1C\x27',       # Bold on - Kanji
    b'\x1C\x2B',       # Bold off - Kanji
]

for seq in sequences:
    ep.write(seq + b'\00')
    ep.write(bytes(repr(seq), 'utf-8') + b": Test text after sequence")
    ep.write(b'\x1B\x40') # reset
    time.sleep(1)

quit_program(None, None, dev)
