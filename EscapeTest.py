#!/usr/bin/env python3

# sequence = [27, 91, 55, 66, 27, 91, 55, 67]
# print("".join(map(chr, sequence)), end="")
# print("Hello World")
# print("".join(map(chr, sequence)))

goto_1_1 = "\x9b1;1H"
clear_screen = "\x9b2J"

print(clear_screen + goto_1_1 + "Lösche Inhalt und springe zum Anfang des Terminals")
