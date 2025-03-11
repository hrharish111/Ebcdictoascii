def read_binary_catalog(data, remotefileinfo, encoding):
    outfile = []
    
    if not remotefileinfo[0].get("Lrecl"):
        for i in data:
            decoded_chunk = decode_ebcdic_char(i, encoding)  # Fixed function name
            outfile.append(decoded_chunk + "\n")
    else:
        lrecl = int(remotefileinfo[0]["Lrecl"])
        recfm = remotefileinfo[0].get("Recfm", "").lower()

        if recfm == "fb":
            i = 0
            while i < len(data):
                chunk = data[i:i + lrecl]
                if not chunk:
                    break
                outfile.append(decode_ebcdic_char(chunk, encoding) + "\n")
                i += lrecl

        elif recfm == "vb":
            i = 0
            while i < len(data):
                if i + 4 > len(data):  # Ensure we have at least 4 bytes for the header
                    break
                record_length = int.from_bytes(data[i:i+2], "big")
                actual_record_length = record_length - 4
                if actual_record_length <= 0 or i + 4 + actual_record_length > len(data):
                    break
                record = data[i+4:i+4+actual_record_length]
                outfile.append(decode_ebcdic_char(record, encoding) + "\n")
                i += 4 + actual_record_length

        else:
            i = 0
            while i < len(data):
                chunk = data[i:i + lrecl]
                if not chunk:
                    break
                outfile.append(decode_ebcdic_char(chunk, encoding) + "\n")
                i += lrecl

    return outfile
