#!/usr/bin/env python3

#--------------------------------------------------------------------------------------
# file_sherpa.py      Modified: Sunday, August 26, 2018 11:14 AM
#
# If Pythonized...
#
#   This Python3 application has its own 'virtual environment'.
#   Follow https://docs.python.org/3/tutorial/venv.html for guidance to create,
#   activate and use it.
#
#   My command sequence was...
#
#     cd ~/file-sherpa; mv -f app app-backup; python3 -m venv app; source app/bin/activate
#     rsync -aruvi app-backup/. app/ --exclude=bin --exclude=include --exclude=lib --exclude=pyvenv.cfg --progress
#     rm -fr app-backup; cd app; curl https://bootstrap.pypa.io/get-pip.py | python3; pip install -r requirements.txt
#
#   Packaging and distribution of this utility should follow the guidance provided at
#     https://packaging.python.org/tutorials/packaging-projects/
#
# If Dockerized...
#
#   This Python3 application should be launched via Docker using the provided
#   file-sherpa.sh Bash script, and Dockerfile.
#
# In either case, for convenience you should define a symbolic link in your path like so:
#
#     sudo ln -s ~/file-sherpa/app/file-sherpa.sh /usr/local/bin/file-sherpa
#
#--------------------------------------------------------------------------------------

#--- Config data here ----------------
VERSION = "1.0.0"
identify = "file-sherpa v{0}".format(VERSION)
available_actions = ['test', 'email']

Archived_EMail = '/Users/mark/_Archived_EMail_'
PDF_Destination = '/Volumes/mark/Documents/consume'
Attachment_Destination = '/Volumes/files/STORAGE/_MAIL'

import sys
import argparse
import os
import socket
import shutil
import time

from colorama import init, Fore, Back, Style

#--------------------------------
def do_email( ):
  # Move .pdf files from Archived_EMail to PDF_Destination one-at-a-time.  Don't move the 'next' file
  # until the destination is empty!

  OK = do_test( )
  if not OK:
    red("Sorry, but the problems indicated above will not allow this process to continue.")
    sys.exit(10)

  # Gather a list of ALL .pdf files in Archived_EMail...
  all_PDFs = []
  for dirpath, dirnames, filenames in os.walk(Archived_EMail):
    for filename in [f for f in filenames if f.endswith(".pdf")]:
      all_PDFs.append(os.path.join(dirpath, filename))

  moved = 0

   # Move PDFs to PDF_Destination
  for fullpath in all_PDFs:
    filename = os.path.basename(fullpath)
    newpath = "{0}/{1}".format(PDF_Destination, filename)
    try:
      dest = shutil.copy(fullpath, newpath)
      if dest:
        moved += 1
        normal("{2}. PDF '{0}' was copied to '{1}'.".format(fullpath, dest, moved))
        os.remove(fullpath)
      else:
        red("PDF '{0}' could not be copied to '{1}'.".format(fullpath, newpath))
    except:
      unexpected()
      raise

    # After moving 10 files, wait for paperless-consume to catch up (number of files in PDF_Destination stops decreasing)
    if moved > 9:
      path, dirs, files = next(os.walk(PDF_Destination))
      previous = len(files)
      time.sleep(1)
      stalled = 0

      while stalled < 50:
        path, dirs, files = next(os.walk(PDF_Destination))
        current = len(files)
        if current < previous:
          previous = current
          stalled = 0
          green('Consume process appears to be running.  {0} files left to process.'.format(current))
        else:
          stalled += 1

      if stalled > 49:
        magenta('Consume process appears to have stalled with {0} files remaining. Moving on.'.format(current))
        moved = 0

  # Build an rsync command to move all remaining contents (attachments) to Attachment_Destination
  cmd = "rsync -aruvi --remove-source-files {0}/* {1}/ --progress".format(Archived_EMail, Attachment_Destination)
  green("Moving attachments via: '{0}'".format(cmd))
  try:
    os.system(cmd)
  except:
    unexpected()
    raise

  # Now, remove any empty directories left behind.
  folders = list(os.walk(Archived_EMail))[1:]

  for folder in folders:
    if not folder[2]:
      try:
        os.rmdir(folder[0])
      except OSError as e:
        magenta('An OSError occured: ' + str(e))
      except:
        unexpected()
        raise


#--------------------------------
def do_test( ):
  # Test that all the necessary directories exist...
  OK = True

  # Test for Archived_EMail
  try:
    found = os.path.isdir(Archived_EMail)
    if found:
      green("The '{0}' exists!".format(Archived_EMail))
    else:
      red("The '{0}' does not currently exist!".format(Archived_EMail))
      OK = False
  except:
    unexpected()
    raise

  # Test for PDF_Destination
  try:
    found = os.path.isdir(PDF_Destination)
    if found:
      green("The '{0}' exists!".format(PDF_Destination))
    else:
      red("The '{0}' does not currently exist!".format(PDF_Destination))
      OK = False
  except:
    unexpected()
    raise

  # Test for Attachment_Destination
  try:
    found = os.path.isdir(Attachment_Destination)
    if found:
      green("The '{0}' exists!".format(Attachment_Destination))
    else:
      red("The '{0}' does not currently exist!".format(Attachment_Destination))
      OK = False
  except:
    unexpected()
    raise

  return OK

#--------------------------------
def red(msg):
  print(Fore.RED + "\n" + msg + "\n" + Style.RESET_ALL)

#--------------------------------
def blue(msg):
  print(Fore.BLUE + msg + Style.RESET_ALL)

# --------------------------------
def green(msg):
  global verbose
  if verbose > 0:
    print(Fore.GREEN + msg + Style.RESET_ALL)

# --------------------------------
def magenta(msg):
  global verbose
  if verbose > 0:
    print(Fore.MAGENTA + msg + Style.RESET_ALL)

#--------------------------------
def yellow(msg):
  global verbose
  if verbose > 1:
    print(Fore.YELLOW + msg + Style.RESET_ALL)

#--------------------------------
def normal(msg):
  global verbose
  if verbose > 2:
    print(Style.RESET_ALL + msg)

#--------------------------------
def debug(msg):
  global verbose
  if verbose > 2:
    print(Fore.CYAN + "DEBUG: " + msg + Style.RESET_ALL)

#--------------------------------
def unexpected( ):
  red("Oh no...")
  print("Unexpected error: ", sys.exc_info()[0])


#--- main -------------------------------------------

if __name__ == "__main__":

  # Init globals here
  cwd = os.getcwd( )
  environ = dict()
  verbose = 0        # print only blue(), a positive color, and red(), it's negative counterpart
  # default
  host = 'Unknown'
  args = dict()
  target = 'Undefined'
  base_dir = cwd
  do_not_repeat = False

  # Parse arguments
  parser = argparse.ArgumentParser(prog='file-sherpa', description='This is file-sherpa!')
  parser.add_argument('action', metavar='action', nargs=1, choices=available_actions,
    help='The action to be performed')
  parser.add_argument('-v', '--verbosity', action='count', help='increase output verbosity (default: OFF)')
  parser.add_argument('--version', action='version', version=identify)
  args = parser.parse_args( )

  # Set verbosity
  if args.verbosity is None:
    verbose = 0                 # print blue/red only
  elif args.verbosity > 2:
    verbose = 3                 # print all (blue/red, green/magenta, yellow, black)
  elif args.verbosity > 1:
    verbose = 2                 # print blue/red plus green/magenta and yellow
  else:
    verbose = 1                 # print blue/red plus green/magenta

  # Get the hostname...
  host = socket.gethostname( )   # Note this does not work when the application is "Dockerized"
  # host = os.environ['HOSTNAME']  # When Dockerized.  Comment out this line if running via Python venv

  # Initialize colorama
  init( )

  # Provide some feedback to the user
  arg_list = " ".join(sys.argv[1:])
  blue("{0} ({1}) called on {2} with arguments: {3}".format(identify, sys.argv[0], host, arg_list))

  # Ok, now we are ready to take 'action'.
  if args.action[0] not in available_actions:
    red("ERROR: Sorry, the specified action '{0}' is not available.".format(args.action[0]))
    sys.exit(10)

  if args.action[0] == 'test':
    verbose = max(verbose, 1)     # ok, we really should see something
    do_test( )

  if args.action[0] == 'email':
    do_email( )

  # All done.  Set working directory back to original.
  os.chdir(cwd)

  blue("That's all folks!")
