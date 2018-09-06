# File-Sherpa

Modified: Wednesday, September 5, 2018 9:39 PM

_File-Sherpa_ is a Python 3 script based largely on _Port-Ability_.  It is designed to help automate the backup and file archival operations I use at home.

## Installation

_File-Sherpa_ is currently dependent on Python 3 (version 3.6 in my case). In CentOS I recommend the process documented for CentOS at https://stackoverflow.com/questions/41328451/ssl-module-in-python-is-not-available-when-installing-package-with-pip3, or for Linux in general try https://www.tecmint.com/install-python-in-linux/ to ensure that Python 3 is installed.

_File-Sherpa_ is built to run from its own Python 3 'virtual environment'.  I created my virtual environment following guidance in https://docs.python.org/3/tutorial/venv.html. My command sequence in OSX (or Linux) was...

```
cd ~
git clone https://github.com/SummittDweller/File-Sherpa.git
cd ~/File-Sherpa
mv -f app app-backup
python3 -m venv app     # assumes 'python3' runs a Python version 3 interpreter.  Mine is version 3.6
source app/bin/activate
rsync -aruvi app-backup/. app/ --exclude=bin --exclude=include --exclude=lib --exclude=pyvenv.cfg --progress
rm -fr app-backup
cd app
curl https://bootstrap.pypa.io/get-pip.py | python3
pip install -r requirements.txt
sudo ln -s ~/File-Sherpa/app/file-sherpa.sh /usr/local/bin/file-sherpa
```

## Usage

Once installed you can open a terminal (command-line) window on your host and type `file-sherpa --help` to see the following:

```
usage: file-sherpa [-h] [-v] [-p] [-a] [--version] action

This is file-sherpa!

positional arguments:
  action             The action to be performed

optional arguments:
  -h, --help         show this help message and exit
  -v, --verbosity    increase output verbosity (default: OFF)
  -p, --skip-pdf     skip PDFs (default: OFF)
  -a, --skip-attach  skip attachment directories (default: OFF)
  --version          show program's version number and exit
  ```

### Actions

Available actions are:

  - **test** -- This action returns information about target directories.  The default target directories/mounts are:

    - Archived_EMail = '/Users/mark/_Archived_EMail_'
    - PDF_Destination = '/Volumes/mark/Documents/consume'
    - Attachment_Destination = '/Volumes/files/STORAGE/_MAIL'  


  - **email** -- This action, by default, will move PDF files representing archived email from the *Archived_EMail* directory to the *PDF_Destination* directory, and attachment directories from the *Archived_EMail* directory to the *Attachment_Destination* directory.

    - Options **-p** and **-a** induce the following changes from the default behavior...  

      - **-a**, **--skip-attach**: Skips the *Attachment_Destination* copy operation.
      - **-p**, **--skip-pdf**: Skips the *PDF_Destination* copy operation.

#### test
@TODO Documentation to be provided.

#### email
@TODO Documentation to be provided.

## Project Structure

```
File-Sherpa  
|--app
  |--file-sherpa.sh
  |--file_sherpa.py         <-- The guts of File-Sherpa
  |--requirements.txt  
|--docs
|--README.md
```


## Notes

Used https://docs.python.org/3/tutorial/venv.html to build the 'app' virtual environment on each node.

Requires Python 3 (with a python3 alias) which I installed in CentOS with help from https://medium.com/@gkmr.aus/python-3-6-x-installation-centos-7-4-55ada041a03
