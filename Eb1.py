import os
import codecs

# --- EBCDIC 277 to ASCII Conversion ---
EBCDIC_277 = 'cp277'  # IBM EBCDIC 277 (Nordic)

def ebcdic_to_ascii(data):
    """Convert EBCDIC bytes to ASCII string."""
    return data.decode(EBCDIC_277, errors="ignore")

def create_packed_bcd(decimal_str):
    """Convert a decimal string to packed BCD bytes."""
    if len(decimal_str) % 2:
        decimal_str = "0" + decimal_str  # Ensure even length
    bcd_bytes = bytearray()
    for i in range(0, len(decimal_str), 2):
        byte = (int(decimal_str[i]) << 4) | int(decimal_str[i + 1])
        bcd_bytes.append(byte)
    return bcd_bytes

def create_zoned_decimal(decimal_str):
    """Convert a decimal string to zoned decimal bytes."""
    zoned_bytes = bytearray()
    for i, digit in enumerate(decimal_str):
        if i == len(decimal_str) - 1:  # Last digit gets sign
            if digit == "-":
                zoned_bytes[-1] = (0xB0 | int(zoned_bytes[-1] & 0x0F))  # Negative
                continue
        zoned_bytes.append(0xF0 | int(digit))  # Standard zoned decimal
    return zoned_bytes

def generate_test_file(filename="test.bin"):
    """Generate a test binary file with EBCDIC ASCII, Packed BCD, and Zoned Decimal."""
    with open(filename, "wb") as f:
        f.write(codecs.encode("Hello", EBCDIC_277))  # EBCDIC encoded ASCII
        f.write(create_packed_bcd("123456"))  # Packed BCD
        f.write(create_zoned_decimal("-789"))  # Zoned Decimal
        f.write(codecs.encode("World", EBCDIC_277))  # More EBCDIC ASCII
    print(f"Test binary file '{filename}' created.")

def is_packed_bcd(byte):
    """Check if a byte is part of packed BCD (each nibble 0-9 or last nibble F)."""
    high_nibble = (byte >> 4) & 0x0F
    low_nibble = byte & 0x0F
    return (0 <= high_nibble <= 9) and (0 <= low_nibble <= 9 or low_nibble == 0x0F)

def is_zoned_decimal(byte):
    """Check if a byte is zoned decimal (high nibble A-F, low nibble 0-9)."""
    high_nibble = (byte >> 4) & 0x0F
    low_nibble = byte & 0x0F
    return (0xA <= high_nibble <= 0xF) and (0 <= low_nibble <= 9)

def unpack_bcd(data):
    """Convert packed BCD bytes to digits."""
    return "".join(f"{(byte >> 4) & 0x0F}{byte & 0x0F}" for byte in data).rstrip("F")

def convert_zoned_decimal(data):
    """Convert zoned decimal bytes to ASCII string."""
    result = []
    for byte in data:
        num = byte & 0x0F
        zone = byte >> 4
        if 0xC <= zone <= 0xF:  # Positive sign
            result.append(str(num))
        elif 0xA <= zone <= 0xB:  # Negative sign
            result.append(f"-{num}")
        else:
            result.append("?")  # Unknown format
    return "".join(result)

def detect_and_decode(binary_data):
    ascii_part = bytearray()
    packed_bcd = []
    zoned_dec = []
    buffer = []  # Temporary buffer for packed BCD/zoned decimal

    i = 0
    while i < len(binary_data):
        byte = binary_data[i]

        if 64 <= byte <= 255:  # EBCDIC printable range
            if buffer:  # If buffer has packed/zoned data, process it first
                if is_packed_bcd(buffer[0]): 
                    packed_bcd.append(unpack_bcd(buffer))
                elif is_zoned_decimal(buffer[0]):
                    zoned_dec.append(convert_zoned_decimal(buffer))
                buffer = []
            ascii_part.append(byte)

        elif is_packed_bcd(byte):  # Potential Packed BCD
            buffer.append(byte)

        elif is_zoned_decimal(byte):  # Potential Zoned Decimal
            buffer.append(byte)

        else:  # Unknown format, flush buffer
            if buffer:
                if is_packed_bcd(buffer[0]): 
                    packed_bcd.append(unpack_bcd(buffer))
                elif is_zoned_decimal(buffer[0]):
                    zoned_dec.append(convert_zoned_decimal(buffer))
                buffer = []

        i += 1

    # Process leftover buffer
    if buffer:
        if is_packed_bcd(buffer[0]): 
            packed_bcd.append(unpack_bcd(buffer))
        elif is_zoned_decimal(buffer[0]):
            zoned_dec.append(convert_zoned_decimal(buffer))

    # Convert extracted EBCDIC ASCII part
    ascii_text = ebcdic_to_ascii(ascii_part)

    return ascii_text, packed_bcd, zoned_dec

def process_binary_file(filename="test.bin"):
    """Read, decode, and save extracted data from an EBCDIC binary file."""
    if not os.path.exists(filename):
        print(f"File '{filename}' not found. Generating test file.")
        generate_test_file(filename)

    with open(filename, "rb") as f:
        binary_data = f.read()

    ascii_text, packed_values, zoned_values = detect_and_decode(binary_data)

    with open("output.txt", "w") as f:
        f.write(f"ASCII (Converted from EBCDIC 277): {ascii_text}\n")
        f.write(f"Packed BCD: {', '.join(packed_values)}\n")
        f.write(f"Zoned Decimal: {', '.join(zoned_values)}\n")

    print("Extraction Complete. Check 'output.txt'.")

# --- TESTING FUNCTION ---
def run_tests():
    """Run automated tests to validate output."""
    process_binary_file()

    with open("output.txt", "r") as f:
        content = f.read()

    expected_ascii = "HelloWorld"
    expected_packed = "123456"
    expected_zoned = "-789"

    assert expected_ascii in content, "ASCII conversion failed!"
    assert expected_packed in content, "Packed BCD extraction failed!"
    assert expected_zoned in content, "Zoned Decimal extraction failed!"

    print("✅ All tests passed successfully!")

# --- RUN SCRIPT & TESTS ---
if __name__ == "__main__":
    run_tests()
