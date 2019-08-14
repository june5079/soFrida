import certifi
import sys
if len(sys.argv) < 2:
    print("Usage: %s [pem file path]" % sys.argv[0])
cafile = certifi.where()
with open(sys.argv[1], "rb") as infile:
    customca = infile.read()
with open(cafile, "ab") as outfile:
    outfile.write(customca)