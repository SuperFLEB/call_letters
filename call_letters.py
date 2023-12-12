#!/usr/bin/env python3

from urllib import request

prefixes = ("K","W")
searchUrls = (
    "https://transition.fcc.gov/fcc-bin/amq?list=4&type=0",
    "https://transition.fcc.gov/fcc-bin/fmq?list=4&type=0",
    "https://transition.fcc.gov/fcc-bin/tvq?list=4&type=0",
)

found = set()

try:
    with open("found_call_letters.txt", "r") as letters_file:
        print("Using letters file")
        found = set(letters_file.read().split("\n"))
except:
    print("Could not open letters file. Calling the FCC...")
    for prefix in prefixes:
        for searchUrl in searchUrls:
            searchUrl = f"{searchUrl}&call={prefix}"
            with request.urlopen(searchUrl) as res:
                print(f"Get {searchUrl}...")
                body = res.read().decode()
                print(f"Got it.")
                found |= {row[1:5].replace(' ', '') for row in body.split("\n")}
    with open("found_call_letters.txt", "w") as letters_file:
        letters_file.write("\n".join(sorted(found)))


class ThreeLetters:
    def __init__(self):
        self.kw = 0
        self.first_two = 0
        self.last = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.last += 1
        if self.last >= 27:
            self.last = 0
            self.first_two += 1

        if self.first_two >= 26**2:
            raise StopIteration

        letters = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return "".join((
            letters[int(self.first_two/26)],
            letters[self.first_two % 26],
            (letters + ('',))[self.last]
        ))


all = {f"W{xxx}" for xxx in ThreeLetters()}
all |= {f"K{xxx}" for xxx in ThreeLetters()}
notfound = [cs.replace(' ', '') for cs in  sorted(all - found)]

with open("not_found_call_letters.txt", "w") as not_found_file:
    not_found_file.write("\n".join(notfound))
