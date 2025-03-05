def unpack_packed_decimal(packed_data):
    """Convert IBM Packed Decimal (COMP-3) to ASCII"""
    result=""
    for byte in packed_data:
        high_nibble = (byte >> 4) & 0x0F
        low_nibble = byte & 0x0F
        result += str(high_nibble)
        if low_nibble in {0xA, 0xB, 0xC, 0xD,0xE,0xF}:
            sign = "-" if low_nibble == 0xD else ""
            return sign + result
        result += str(low_nibble)
    return result

def decode_zone_decimal(zoned_data):
    """convert IBM zoned decimal to ascii string"""
    result = ""
    for byte in zoned_data:
        digit = byte & 0x0F #Extract numeric part
        result += str(digit)
    return result

def decode_mixed_binary(data,encoding):
    """ Automatically detect and decode EBCDIC, packed decimal zone decimal fields"""
    result = ""
    i=0
    while i < len(data):
        byte = data[i]
        if 0x40 <=byte <= 0xFF: # EBCDIC range
            result += codecs.decode(bytes([byte]),encoding,errors='ignore')
            i +=1

        elif i+1 < len(data) and data[i+1] in {0xc,0xD,0xF}:
            packed_length = 2 #start with at least 2 bytes
            while i + packed_length < len(data) and data[i + packed_length] not in  {0xC, 0xD, 0xF}:
                packed_length +=1
            packed_value = unpack_packed_decimal(data[i:1 + packed_length])
            result += " " + packed_value
            i += packed_length

        # Zoned Decimal (COBOL DISPLAY NUMERIC)
        elif 0xC0 <= byte <= 0xCF or 0xD0 <= byte <=0xDF or 0xF0 <= byte <= 0xF9:
            zoned_length = 1
            while i + zoned_length < len(data) and 0xF0 <= data[i+ zoned_length] < 0xF9:
                zoned_length +=1
            zoned_value = decode_zone_decimal(data[i:i + zoned_length])
            result += " " + zoned_value
            i += zoned_length

        else:
            result += "?"
            i += 1

    return result.strip()
