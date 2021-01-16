#!/usr/bin/env python3

import getpass
import random
import sys
import textwrap
import time


border_text   = '#-------------------------------------------------#'
greeting_text = 'WELCOME TO THE UNHACKABLE SLO-MATIC SECUROTRON 9000'
processing_text = '... processing\n' * 5
loading_text = '... loading\n' * 5
success_text = '... succeeding\n' * 5


def slow_print(text):
    for char in text:
        print(char, end='')
        sys.stdout.flush()
        time.sleep(0.3)  # short pause for every char

        if random.random() > 0.85:
            time.sleep(0.3)  # more pause occasionally

    print('')  # don't forget a newline


while True:
    slow_print(border_text)
    slow_print(greeting_text)
    slow_print(border_text)
    password = getpass.getpass()
    slow_print(processing_text)
    slow_print(loading_text)
    if password.strip() == open('PASS.txt').read().strip():
        slow_print(success_text)
        break
