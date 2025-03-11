import struct

def readwithchunkwithoutnoisefilter(filename, outputpath, remotefileinfo, encoding="cp500"):
    """ Reads an EBCDIC-encoded file and writes the decoded content to an output file in UTF-8. """

    def decode_and_write(data, outfile):
        """ Helper function to decode and write data to the output file """
        outfile.write(decode_ebcdic_char(data, encoding) + "\n")

    try:
        with open(filename, "rb") as readingbinarymode, open(outputpath, 'w', encoding='utf-8') as outfile:
            file_info = remotefileinfo[0]
            lrecl = file_info.get("Lrecl")
            recfm = file_info.get("Recfm", "").lower()

            if not lrecl:  # Process line by line if Lrecl is not provided
                for line in readingbinarymode:
                    decode_and_write(line, outfile)
                return

            if recfm == "fb":  # Fixed Block format
                record_length = int(lrecl)
                while chunk := readingbinarymode.read(record_length):
                    decode_and_write(chunk, outfile)

            elif recfm == "vb":  # Variable Block format
                while True:
                    header = readingbinarymode.read(4)
                    if len(header) < 4:
                        break
                    record_length = int.from_bytes(header[:2], "big")
                    actual_record_length = record_length - 4
                    if actual_record_length <= 0:
                        break
                    record = readingbinarymode.read(actual_record_length)
                    decode_and_write(record, outfile)

            else:  # Handle invalid Recfm values
                raise ValueError(f"Unsupported Recfm format: {recfm}")

    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Error processing file: {e}")
