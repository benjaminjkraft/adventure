# TEXT ADVENTURE QUINE
# See puzzle: https://galacticpuzzlehunt.com/puzzle/adventure
#
# By walking around the puzzle, we find it is a keyboard, and we learn the
# following instructions:
#     e, w, nw, ne, sw, se: move those directions (hex grid)
#     t: clear the blackboard, and write the rest of the line to it
#     r: read/execute the instructions on the blackboard
#     p: press the button in this room
#     v: turn on verbose mode
# (There are some others, but we won't need them.) Our goal is to make a quine:
# a program which presses, in order, the buttons corresponding to its own code.
#
# From here on, we ignore ne/sw, and draw on a square grid, to simplify.  We
# label the grid as follows (_ is unused keys):
#     [ R1 ] [ S1 ] [ T1 ] [ W1 ] [ZZZ1] [ E1 ] [ P1 ] [ N1 ] [____] [____]
#     [ R2 ] [ S2 ] [ T2 ] [ W2 ] [ZZZ2] [ E2 ] [ P2 ] [ N2 ] [____]
#     [____] [____] [____] [____] [CODA] [____] [____]
# This layout consists of two rows, in parallel structure with a "ZZZ" key and
# a key for each command we will need, plus the CODA key.
#
# In the first row, we write on R1's chalkboard the instructions to start at
# R1, walk to the R key (which happens to be R2), press it ('p'), and walk back
# to R2, and so on for each key.  That is, each chalkboard has instructions to
# type the corresponding key and return to that chalkboard.  So if we're at
# ZZZ1, we can type 'r' by walking to R1, reading it ('r'), and then walking
# back.
#
# In the second row, we write on R2's chalkboard the instructions to type the
# following sequence: the keys needed to get from ZZZ1 to R1, then read it
# ('r'), then those to return to ZZZ1.  (Again, we return to R2 after typing.)
# That is, each chalkboard has the instructions necessary to type the sequence
# of keys needed to type the key corresponding to the chalkboard, starting at
# ZZZ1 and using the first row's chalkboards to do the typing.
#
# To put it another way, there exists a sequence of keys (namely walk to the
# right spot on the first row, 'r', then walk back) which if executed at ZZZ1
# will type a given key, and if executed at ZZZ2 will type itself.  This is the
# core of our quine.
#
# We'll talk about exactly what we write on ZZZ2 and CODA later, but they'll be
# short and concrete sequences.
#
# Now consider the string S consisting of the characters needed to:
#   - write everything we need on all the boards except ZZZ1
#   - walk back to ZZZ1
#
# Let's first run S -- setting up everything else.  Then, write on ZZZ1's board
# the characters needed to type out S using the first row.  Now, run that board
# -- this types out S.  Finally, run it again, this time starting from ZZZ2 --
# this types out the sequence on ZZZ1's board itself.
#
# There are a couple more bits we need to consider.  First, there's a 't'
# needed after all the other setup to start writing on ZZZ1's board -- so let's
# append that to S.
#
# Second, we can't run the code on ZZZ1's board at ZZZ2 without some tricks.
# Here's our trick: before doing its thing, the code on ZZZ1's board will walk
# to ZZZ2 and read it.  The first time we execute ZZZ1, we'll ensure that ZZZ2
# has instructions to walk back to ZZZ1; then the second time we'll leave it
# empty.  This way, the rest of ZZZ1's instructions execute at ZZZ1 the first
# time, and ZZZ2 the second time.  Again, we need to type these before writing
# anything else on ZZZ1, so append them to S.
#
# Finally, we need to run some code at the end: namely, 'r' to execute ZZZ1 the
# first time, then commands to walk over to ZZZ2, clear its board, and walk
# back.  We'll use CODA to type these extra commands.  So we write on CODA the
# commands necessary to type the following:
#   - 'r' (to execute ZZZ1)
#   - 'eeet' (walk to ZZZ2, clear it)
#   - 'wwwr' (walk back to ZZZ1, execute again, this time ending at ZZZ2)
#   - 'eer' (walk to CODA, execute it)
#
# So here's our program:
#   Let S be the characters needed to:
#     - write everything we need on all the boards except ZZZ1
#       (but including ZZZ2 and CODA)
#     - walk back to ZZZ1
#     - type 'teee'
#   And let CODA be the following two commands:
#     - 'reeet'
#     - 'wwwreer'
# Our program is:
#     - S
#     - the code needed to type S using the first row, starting at ZZZ1
#     - CODA
#
# See program.txt for all of that spelled out.

import sys


# Keyboard
QWERTY = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']

# Q is 0, 0; W is 1, 0
KEY_AT = {(i, j): c
          for j, line in enumerate(QWERTY)
          for i, c in enumerate(line)}

LOC_OF = {c: (i, j)
          for j, line in enumerate(QWERTY)
          for i, c in enumerate(line)}


def _sgn(n):
    return n / abs(n)


def walk(offset):
    x, y = offset
    if x > 0 and y < 0:
        return 'ne' + walk((x - 1, y + 1))
    elif x < 0 and y > 0:
        return 'sw' + walk((x + 1, y - 1))
    elif y > 0:
        return 'se' + walk((x, y - 1))
    elif y < 0:
        return 'nw' + walk((x, y + 1))
    elif x < 0:
        return 'w' + walk((x + 1, y))
    elif x > 0:
        return 'e' + walk((x - 1, y))
    else:  # x == 0 and y == 0
        return ''


def add(offset1, offset2):
    return (offset1[0] + offset2[0], offset1[1] + offset2[1])


def sub(offset1, offset2):
    return (offset1[0] - offset2[0], offset1[1] - offset2[1])


def neg(offset):
    return sub((0, 0), offset)


def press(keys, start='h', end=None):
    """Press a key, starting and ending at given locations."""
    end = LOC_OF[end or start]
    start = LOC_OF[start]
    ret = ''
    prev = start
    for key in keys:
        if key.isspace():
            continue
        loc = LOC_OF[key]
        ret += walk(sub(loc, prev))
        ret += 'p'
        prev = loc
    ret += walk(sub(end, prev))
    return ret


MAPPING = ['rstw epn']
OFFSET = (0, 1)
CODA_OFFSET = (0, 1)
ZZZ1_KEY = next(k
                for ms, ks in zip(MAPPING, QWERTY)
                for m, k in zip(ms, ks)
                if m == ' ')
ZZZ2_KEY = KEY_AT[add(OFFSET, LOC_OF[ZZZ1_KEY])]
CODA_KEY = KEY_AT[add(CODA_OFFSET, LOC_OF[ZZZ2_KEY])]
MAPPING_LOC_OF = {
    k: sub((x, y), LOC_OF[ZZZ1_KEY])
    for y, row in enumerate(MAPPING)
    for x, k in enumerate(row)
    if k != ' '}

CODA = ('\nr' + walk(OFFSET)
        + 't\n' + walk(neg(OFFSET))
        + 'r' + walk(CODA_OFFSET) + 'r')

ROW1 = {
    KEY_AT[(x, y)]: press(k, KEY_AT[(x, y)])
    for y, row in enumerate(MAPPING)
    for x, k in enumerate(row)
    if k != ' '}
ROW2 = {
    KEY_AT[add((x, y), OFFSET)]: press(
        (walk(sub((x, y), LOC_OF[ZZZ1_KEY]))
         + 'r' + walk(sub(LOC_OF[ZZZ1_KEY], (x, y)))),
        KEY_AT[add((x, y), OFFSET)])
    for y, row in enumerate(MAPPING)
    for x, k in enumerate(row)
    if k != ' '}
EXTRA = {
    ZZZ2_KEY: walk(neg(OFFSET)),                     # ZZZ2
    CODA_KEY: press(CODA, CODA_KEY, end=CODA[-1]),   # CODA
}

# What we want to put on each board, except ZZZ1
BOARDS = {}
BOARDS.update(ROW1)
BOARDS.update(ROW2)
BOARDS.update(EXTRA)


def write(text, at, start='h'):
    """Write text on a board (and stay there)."""
    start = LOC_OF[start]
    at = LOC_OF[at]
    return walk(sub(at, start)) + ' t ' + text + '\n'


def write_all(boards, start='h', end=ZZZ1_KEY):
    """Write text on a bunch of boards the boards."""
    end = end or start
    prev = start
    ret = ''
    for k, text in sorted(boards.items(), key=lambda i: LOC_OF[i[0]]):
        ret += write(text, k, prev)
        prev = k
    ret += walk(sub(LOC_OF[end], LOC_OF[prev]))
    return ret


def press_row1(keys):
    """Starting at ZZZ1, press these keys via the first row."""
    start = (0, 0)
    ret = ''
    for key in keys:
        if key.isspace():
            continue
        loc = MAPPING_LOC_OF[key]
        ret += walk(sub(loc, start))
        ret += 'r'
        ret += walk(sub(start, loc))
    return ret


S = write_all(BOARDS) + ' t ' + walk(OFFSET) + 'r'
PROG = S + ' ' + press_row1(S) + CODA

print PROG
print >>sys.stderr, "Lines:", PROG.count('\n') + 1
print >>sys.stderr, "Commands:", len(PROG.replace(' ', '').replace('\n', ''))
