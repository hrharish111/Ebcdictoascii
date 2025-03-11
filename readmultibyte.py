def readninarycatlog(data,remotefileinfo,encoding):
    outfile = []
    if not remotefileinfo[0].get("Lrecl"):
            for i in data:
                decoded_chunk = decode_ebcic_char(i,encoding)
                removedspace = decoded_chunk+"\n"
                outfile.append(removedspace)
    else:
        if remotefileinfo[0].get("Recfm").lower() == "fb":
            i = 0
            while i < len(data):
                chunk = data[i:i+int(remotefileinfo[0]["Lrecl"])]
                if not chunk:
                    break
                removedspace = decode_ebcic_char(chunk, encoding) + "\n"
                outfile.append(removedspace)
                i += int(remotefileinfo[0]["Lrecl"])

        elif remotefileinfo[0].get("Recfm").lower() == "vb":
            while True:
                header = readingbinarymode.read(4)
                if len(header) < 4:
                    break
                # record_length = struct.unpack(">H", header[:2])[0]
                record_length = int.from_bytes(header[:2], "big")
                actual_record_length = record_length - 4
                if actual_record_length <= 0:
                    break
                record = readingbinarymode.read(actual_record_length)
                removedspace = decode_ebcic_char(record, encoding) + "\n"
                outfile.write(removedspace)
        else:
            i = 0
            while i < len(data):
                chunk = data[i: i+ int(remotefileinfo[0]["Lrecl"])]
                if not chunk:
                    break
                removedspace = decode_ebcic_char(chunk, encoding) + "\n"
                outfile.append(removedspace)
                i+=int(remotefileinfo[0]["Lrecl"])
