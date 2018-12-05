# This file is used to get schedule of tutoring
import re
import html2text
import urllib

fp = urllib.request.urlopen("https://hknpolito.org/tutoring/")
mybytes = fp.read()

mystr = mybytes.decode("utf8")
fp.close()
mystr = html2text.html2text(mystr)
m=mystr.split("* ###")
m.pop(0)
for el in m:
    sub_els=el.split('\n',7)
    sub_els.pop()
    print("----------------")
    for sub_el in sub_els:
        print(sub_el)
