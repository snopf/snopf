To build all host programs (command line tool, qt-tool, browser extensions) 
just use (being in the python venv!)
$ make

To build specific tools go to the subfolders and run
$ make tool

All binaries are put into dist/

To install for linux:

1. USB rule:
To use the snopf device you should create an entry in /etc/udev/rules.d.
You can just run 
$ sudo ./install_usb_rule.sh
(Needs root privileges for writing to /etc/)

2. Driver for the browser extensions (chrome or firefox):
$ ./install_native_app.sh

3. Command line (snopf_cmd) and qt tool (snopf_manager):
$ ./install.sh
