import string

def is_ascii(byte):
    """Check if byte is a printable ASCII character."""
        return 32 <= byte <= 126

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
                                                                                                                                                ascii_str = []
                                                                                                                                                    packed_bcd = []
                                                                                                                                                        zoned_dec = []
                                                                                                                                                            buffer = []  # Temporary buffer for packed BCD/zoned decimal

                                                                                                                                                                def process_buffer():
                                                                                                                                                                        nonlocal buffer
                                                                                                                                                                                if buffer:
                                                                                                                                                                                            if is_packed_bcd(buffer[0]): 
                                                                                                                                                                                                            packed_bcd.append(unpack_bcd(buffer))
                                                                                                                                                                                                                        elif is_zoned_decimal(buffer[0]):
                                                                                                                                                                                                                                        zoned_dec.append(convert_zoned_decimal(buffer))
                                                                                                                                                                                                                                                    buffer = []

                                                                                                                                                                                                                                                        i = 0
                                                                                                                                                                                                                                                            while i < len(binary_data):
                                                                                                                                                                                                                                                                    byte = binary_data[i]

                                                                                                                                                                                                                                                                            if is_ascii(byte):  # ASCII
                                                                                                                                                                                                                                                                                        process_buffer()
                                                                                                                                                                                                                                                                                                    ascii_str.append(chr(byte))

                                                                                                                                                                                                                                                                                                            elif is_packed_bcd(byte) or is_zoned_decimal(byte):  # Packed BCD or Zoned Decimal
                                                                                                                                                                                                                                                                                                                        buffer.append(byte)

                                                                                                                                                                                                                                                                                                                                else:  # Unknown format, flush buffer
                                                                                                                                                                                                                                                                                                                                            process_buffer()

                                                                                                                                                                                                                                                                                                                                                    i += 1

                                                                                                                                                                                                                                                                                                                                                        # Process leftover buffer
                                                                                                                                                                                                                                                                                                                                                            process_buffer()

                                                                                                                                                                                                                                                                                                                                                                return "".join(ascii_str), packed_bcd, zoned_dec

                                                                                                                                                                                                                                                                                                                                                                # --- Example Usage ---
                                                                                                                                                                                                                                                                                                                                                                with open("input.bin", "rb") as f:
                                                                                                                                                                                                                                                                                                                                                                    binary_data = f.read()

                                                                                                                                                                                                                                                                                                                                                                    ascii_text, packed_values, zoned_values = detect_and_decode(binary_data)

                                                                                                                                                                                                                                                                                                                                                                    # Save extracted data
                                                                                                                                                                                                                                                                                                                                                                    with open("output.txt", "w") as f:
                                                                                                                                                                                                                                                                                                                                                                        f.write(f"ASCII: {ascii_text}\n")
                                                                                                                                                                                                                                                                                                                                                                            f.write(f"Packed BCD: {', '.join(packed_values)}\n")
                                                                                                                                                                                                                                                                                                                                                                                f.write(f"Zoned Decimal: {', '.join(zoned_values)}\n")

                                                                                                                                                                                                                                                                                                                                                                                print("Extraction Complete. Check output.txt")