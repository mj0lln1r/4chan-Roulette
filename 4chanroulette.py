#!/usr/bin/python

import random, sys, getopt, time, json, urllib.request, subprocess, threading

# Like it's a real program or something...
def usage():
    print("OPTIONS:")
    print("\t-w, --work-safe\tOnly go to worksafe boards (default will give you either)")
    print("\t-b <board>\tAttempt to specify board (overrides worksafe argument)")
    print("\t-s <search>\tWith -b (or without) attempt to find thread related to search term")
    print("\t-l, --words\tHave the progress bar print 4chans while fetching thread.")
    print("\t-h, --help\tDisplay this very text!")

# Main event, so to speak
def get_random_thread(usr_board, search_term, worksafe=False):
    # Get list of boards, load data
    boards_json = urllib.request.urlopen("http://api.4chan.org/boards.json")
    board_data = json.loads(boards_json.read().decode("utf-8"))["boards"]

    all_boards = [ x["board"] for x in board_data ]

    # Get a board from API's list, or from the user if they specified one.
    if ( usr_board not in all_boards ):
        if (worksafe):
            boards = [ x["board"] for x in board_data if x["ws_board"] == 1 ]
        else:
            boards = all_boards
        board = random.choice(boards)
    else:
        board = usr_board

    boards_json.close()

    # Get list of threads on board from catalog.json :: moot, the catalog is the best idea ever!
    threads_json = urllib.request.urlopen("http://api.4chan.org/" + board + "/catalog.json") 
    threads = json.loads(threads_json.read().decode("utf-8"))

    # Thread Search if search term is present
    found = False
    
    if not ( search_term == "NOTHING" ):
        matching_threads = []
        for page in threads:
            for athread in page["threads"]:
                # Search OPs' comments and subject lines for search terms
                com = "com" in athread and search_term.lower() not in athread["com"].lower()
                sub = "sub" in athread and search_term.lower() not in athread["sub"].lower()
                name = "name" in athread and search_term.lower() not in athread["name"].lower()
                if (com or sub or name):
                    continue
                # Don't add a thread to the list just because there's nothing to search!
                elif ("com" not in athread and "sub" not in athread and "name" not in athread):
                    continue
                else:
                    matching_threads.append(athread)
                    found = True
                    
    if (found):            
        thread = random.choice(matching_threads)
    else:
        # Or just get a random thread on a random page, that's cool too.
        page = random.choice(threads)["threads"]
        thread = random.choice(page)
        
    threads_json.close()

    # Put the board and thread together into a URL...
    result = "https://boards.4chan.org/" + board + "/res/" + str(thread["no"])

    # And copypasta it to the clipboard!
    clipboard = subprocess.Popen(["xsel", "-bi"], stdin=subprocess.PIPE)
    clipboard.communicate(input = bytes(result, "utf-8"))

# Prints both 4channy and lame ordinary types of progressbar to stdout
def progress(lex):
    sys.stdout.write("[%s]" % (" " * 30))
    sys.stdout.flush()
    sys.stdout.write("\b" * (31))

    words = [ 'moot♥', '4chan', 'faggot', 'jimprofit', '~Desu', 'mods=gods=',
              'lulz', '/b/', 'meme', 'C-C-C-C-COMBO B-B-B-B-Breaker!']

    wat = random.choice(words)
    for f in range(0, 30):    
        time.sleep(0.1)
        if (lex):
            sys.stdout.write(wat[ f % len(wat) ])
        else:
            sys.stdout.write("#")
        sys.stdout.flush()
        
    sys.stdout.write("\n")

# Variables acted on by command options
def main():
    worksafe, lex, usr_board, search = False, False, "NOTHING", "NOTHING"
    
    #Setup getopt options, and do as the user commands
    try:
        opts, args = getopt.getopt(sys.argv[1:], "wb:s:lh", ["work-safe", "words", "help"])
    except getopt.GetoptError as err:
        print( str(err))
        sys.exit(2)

    for o, a in opts:
        if o in ( "-w", "--work-safe" ):
            worksafe = True
        elif o in ( "-b" ):
            usr_board = a
        elif o in ( "-s" ):
            search = a
        elif o in ( "-l", "--words" ):
            lex = True
        elif o in ( "-h", "--help" ):
            usage()
            sys.exit(0)
        else:
            assert False, "unhandled option"

# Start thread which gets the other kind of thread
    t = threading.Thread( target = get_random_thread, args=( usr_board, search, worksafe ))
    t.start()

    print("Reading the 4chans...\n")
    
    # Print status bars while waiting
    while (t.is_alive()):
        progress(lex)
        t.join(0.1)
        
    print("\nYou have a thread!")

if ( __name__ == "__main__" ):
    main()
