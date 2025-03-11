def readwithchunkwithoutnoisefilter(filename,outputpath,remotefileinfo,encoding="cp500"):
    with open(filename,"rb") as readingbinarymode, open(outputpath, 'w',encoding='utf-8') as outfile:
        if not remotefileinfo[0].get("Lrecl"):
            for i in readingbinarymode:
                decoded_chunk = decode_ebcdic_char(i,encoding)
                removedspace = decoded_chunk+"\n"
                outfile.write(removedspace)
        else:
            if remotefileinfo[0].get("Recfm").lower()=="fb":
                while True:
                   chunk = readingbinarymode.read(int(remotefileinfo[0]["Lrecl"]))
                   if not chunk:
                      break
                   removedspace = decode_ebcdic_char(chunk,encoding)+"\n"
                   outfile.write(removedspace)
            elif remotefileinfo[0].get("Recfm").lower()=="vb":
                while True:
                    header =readingbinarymode.read(4)
                    if len(header)<4:
                        break
                    #record_length = struct.unpack(">H", header[:2])[0]
                    record_length = int.from_bytes(header[:2],"big")
                    actual_record_length = record_length - 4
                    if actual_record_length <= 0 :
                        break
                    record = readingbinarymode.read(actual_record_length)
                    removedspace = decode_ebcdic_char(record,encoding)+"\n"
                    outfile.write(removedspace)
            else:
                while True:
                   chunk = readingbinarymode.read(int(remotefileinfo[0]["Lrecl"]))
                   if not chunk:
                      break
                   removedspace = decode_ebcdic_char(chunk,encoding)+"\n"
                   outfile.write(removedspace)
