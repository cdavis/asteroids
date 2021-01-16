#!/usr/bin/env python3

import time
time.sleep = lambda _: None
def open(file):
  print("YA")

  return realopen("chicken.txt")

realopen = __builtins__.open
__builtins__.open = open
import passgame
