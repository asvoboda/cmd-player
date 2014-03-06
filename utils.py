import os
import sys


def get_filename(f):
    name = None
    exts = ("mp3", "wav", "m4a", "MP3", "WAV", "M4A")
    if os.path.isfile(f):
        if f.endswith(exts):
            name = os.path.join(os.getcwd(), f)
        else:
            print("Not a valid media type")
    else:
        print("%s is not a valid thing" % f)
    return name


def find_largest_in_common(others, start_string):
    rest = min(others, key=len)
    largest_length = len(rest)
    build = start_string
    pos = 0

    while len(build) < largest_length:
        good = True
        for item in others:
            pos = len(build)
            if rest[pos] != item[pos]:
                good = False
        if good:
            build += rest[pos]
        else:
            break

    return build


def format_columns(mylist, cols):
    col_width = max(len(word) for word in mylist) + 2  # padding
    template = ""
    for i in range(cols):
        template += "{%s:%s}" % (i, col_width)

    data = []
    for i in range(0, len(mylist), cols):
        data.append(mylist[i:i + cols])

    for row in data:
        try:
            print
            template.format(*row)
        except IndexError:
            #last row might be too small for the template
            for k in range(cols - 1, 0, -1):
                try:
                    new_template = ""
                    for i in range(k):
                        new_template += "{%s:%s}" % (i, col_width)
                    print
                    new_template.format(*row)
                    break
                except IndexError:
                    continue


def tab_complete(start_string, show):
    list = os.listdir(os.getcwd())
    count = 0
    rest = ""
    others = []
    for item in list:
        if item.startswith(start_string):
            others.append(item)
            if count == 0:
                rest = item
            count += 1
    if count > 1:
        if show:
            rest = ", ".join(others)
        else:
            rest = find_largest_in_common(others, start_string)
    return count, rest


def handle_whitespace_chars(msg, input, last_input):
    if input == "\b" and msg:
        msg = msg[:-1]
        sys.stdout.write("\r" + msg + " " + "\b")
    elif input == "\t":
        split = msg.split()
        to_complete = " ".join(split[1:])
        the_rest = split[0]
        if last_input == "\t":
            num, to_print = tab_complete(to_complete, True)
            msg = to_print
        else:
            num, to_print = tab_complete(to_complete, False)
            msg = the_rest + " " + to_print
        sys.stdout.write("\r" + msg)
    elif input != "\r":
        msg += input
        sys.stdout.write("\r" + msg)
    else:
        print("\n")
        return msg, True
    return msg, False