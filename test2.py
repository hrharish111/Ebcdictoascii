import codecs

EBCDIC_277 = 'cp277'  # IBM EBCDIC 277 (Nordic)

def ebcdic_to_ascii(data):
    """Convert EBCDIC bytes to ASCII string."""
    return data.decode(EBCDIC_277, errors="ignore")

def unpack_packed_decimal(packed_data):
    """Convert IBM Packed Decimal (COMP-3) to ASCII"""
    result = ""
    sign = ""

    for i, byte in enumerate(packed_data):
        high_nibble = (byte >> 4) & 0x0F
        low_nibble = byte & 0x0F

        if i == len(packed_data) - 1:  # Last byte contains the sign
            if low_nibble in {0xA, 0xB, 0xC, 0xE, 0xF}:  # Positive
                sign = "+"  
            elif low_nibble == 0xD:  # Negative
                sign = "-"
            result += str(high_nibble)
        else:
            result += str(high_nibble) + str(low_nibble)

    return sign + result

def decode_zoned_decimal(zoned_data):
    """Convert IBM Zoned Decimal to ASCII string with sign handling."""
    result = []
    sign = "+"

    for i, byte in enumerate(zoned_data):
        digit = byte & 0x0F
        zone = byte >> 4

        if i == len(zoned_data) - 1:  # Last byte determines sign
            if zone in {0xA, 0xB, 0xD}:  # Negative sign
                sign = "-"
            elif zone in {0xC, 0xE, 0xF}:  # Positive sign
                sign = "+"
        
        result.append(str(digit))

    return sign + "".join(result)

def decode_mixed_binary(data):
    """Detect and decode EBCDIC, Packed Decimal, and Zoned Decimal fields."""
    result = ""
    i = 0

    while i < len(data):
        byte = data[i]

        # Skip control bytes like `\xC4` if not meaningful
        if byte in {0xC4, 0x00, 0x60}:  # Likely control characters
            i += 1
            continue  

        # **EBCDIC Text Conversion**
        if 0x40 <= byte <= 0xFF:
            result += ebcdic_to_ascii(bytes([byte]))
            i += 1

        # **Detect Packed Decimal (COMP-3)**
        elif i + 1 < len(data) and data[i + 1] in {0xC, 0xD, 0xF}:
            packed_length = 2
            while i + packed_length < len(data) and data[i + packed_length] not in {0xC, 0xD, 0xF}:
                packed_length += 1
            packed_value = unpack_packed_decimal(data[i: i + packed_length])
            result += " " + packed_value
            i += packed_length

        # **Detect Zoned Decimal**
        elif 0xC0 <= byte <= 0xCF or 0xD0 <= byte <= 0xDF or 0xF0 <= byte <= 0xF9:
            zoned_length = 1
            while i + zoned_length < len(data) and 0xF0 <= data[i + zoned_length] <= 0xF9:
                zoned_length += 1
            zoned_value = decode_zoned_decimal(data[i: i + zoned_length])
            result += " " + zoned_value
            i += zoned_length

        else:
            result += "?"
            i += 1

    return result.strip()

# **Test the function with your binary data**
binary_data = b"\xc4\xd2\xd2\x00\x04L\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x0c\xf2\xf0\xf2\xf3`\xf1\xf2`\xf2\xf9`\xf1\xf7K\xf1\xf6K\xf4\xf5K\xf7\xf8\xf5\xf1\xf1\xf7\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x0c\xf2\xf0\xf2\xf3`\xf1\xf2`\xf2\xf9`\xf1\xf7K\xf1\xf6K\xf4\xf5K\xf7\xf8\xf5\xf1\xf1\xf7\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x08\x18T\x9d\xf2\xf0\xf2\xf3`\xf1\xf2`\xf2\xf9`\xf1\xf7K\xf1\xf6K\xf4\xf5K\xf7\xf8\xf5\xf1\xf1\xf7\x00\x00\x00\x00\x00\x00\x00\x00\x0c\xf2\xf0\xf2\xf3`\xf1\xf2`\xf2\xf9`\xf1\xf7K\xf1\xf6K\xf4\xf5K\xf7\xf8\xf5\xf1\xf1\xf7\x00\x00\x00\x00\x00\x00\x00\x00\x0c\xf2\xf0\xf2\xf3`\xf1\xf2`\xf2\xf9`\xf1\xf7K\xf1\xf6K\xf4\xf5K\xf7\xf8\xf5\xf1\xf1\xf7\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x08!$\x9c\x00\x00\x00\x00\x00\x00\x00\x0c"

decoded_output = decode_mixed_binary(binary_data)
print(decoded_output)
