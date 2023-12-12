#!/usr/bin/env python3

# Using information from FCC website searches, this finds all Kxxx/Wxxx call-signs in use
# (results/found_call_letters.txt), derives all call-signs that are not currently in use
# (results/not_found_call_letters.txt), and any call-signs that spell words at the end
# (results/<found/not_found>_<number>_letter_words.txt).
#
# Use this if you're trying to make up a fake radio or TV station, and you don't want to step on a real one,
# for instance. (Of course, check more thoroughly after the fact. Things change, and the FCC database might not be
# exhaustive.)
#
# To re-fetch all the call signs again, remove everything in the "results" directory, and it'll be retrieved and
# regenerated again.

from urllib import request

prefixes = ("K","W")
searchUrls = (
    "https://transition.fcc.gov/fcc-bin/amq?list=4&type=0",
    "https://transition.fcc.gov/fcc-bin/fmq?list=4&type=0",
    "https://transition.fcc.gov/fcc-bin/tvq?list=4&type=0",
)

found = set()

try:
    with open("results/found_call_letters.txt", "r") as letters_file:
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

with open("results/not_found_call_letters.txt", "w") as not_found_file:
    not_found_file.write("\n".join(notfound))


try:
    with open('3rdparty/2-3-kw4-letter-words.txt', 'r') as words_file:
        all_words = [line for line in words_file.read().split("\n") if line]
        all_words.sort()
        words_by_length = (
            {w for w in all_words if len(w) == 2},
            {w for w in all_words if len(w) == 3},
            {w for w in all_words if len(w) == 4}
        )
except:
    print("Could not open words file. Skipping word list generation.")
    exit()

for name, calls in {"found": list(found), "not_found": notfound}.items():
    for index, word_set in enumerate(words_by_length):
        size = index + 2
        results = [c for c in calls if c[4-size:] in word_set]
        results.sort()

        with open(f"results/{name}_{size}_letter_words_call_letters.txt", "w") as output_file:
           output_file.write("\n".join(results))
           output_file.write("\n")

