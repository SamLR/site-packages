#!/usr/bin/python
"""
Generate sensible, readable passwords
"""

import string
import random
import argparse

def gen_password(length, char_set):
  """
  Generate a password of given length from the supplied character set.
  """
  return "".join(random.choice(char_set) for x in range(length))

def parse_arguments():
  parser = argparse.ArgumentParser(description="Generate passwords")
  parser.add_argument("-t","--test", action="store_true", help="Run the internal tests")
  parser.add_argument("-a","--all_char", action="store_true", help="Use all available ascii character")
  
  parser.add_argument('-l', default=8, help="The length of the password", type=int)
  args = parser.parse_args()
  return args

def get_char_set(all_char=False):
  char_set = list(string.printable) if all_char else list(string.letters + string.digits)
  to_remove = string.whitespace if all_char else ("1", "l", "I", "0", "O", "o")
  for c in to_remove:
    char_set.remove(c)
  return char_set
  
def test():
  print "The 'readable' char set is:", get_char_set(all_char=False)
  print "The full (non-whitespace) char set is:", get_char_set(all_char=True)
  dumb = gen_password(8,"A")
  assert len(dumb)==8
  for i in dumb: assert i == "A"
  print "A basic 8 character readable password:", gen_password(8,get_char_set(all_char=False))

if __name__=="__main__":
  args=parse_arguments()
  char_set = get_char_set(args.all_char)
  
  if args.test:
    test()
  else:
    print gen_password(args.l, char_set)