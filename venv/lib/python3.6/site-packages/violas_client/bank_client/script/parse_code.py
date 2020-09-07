import sys
import json
import os
from canoser import bytes_to_int_list

file_name = sys.argv[1]
file = open(file_name, "a+")
for path in sys.argv[2:]:
    with open(path, "rb") as input:
         code = input.read()
         file.write("\"")
         file.write(os.path.basename(path)[:-3])
         file.write("\"")
         file.write(": ")
         file.write(str(code))
         file.write(",\n")
