To build all programs (qt-tool, browser extensions) just use (being in the python venv!)
$ make

To build specific tools go to the subfolders and run
$ make tool

All binaries are put into dist/

USB rule installation (Linux):
To use the snopf device you should create an entry in /etc/udev/rules.d.
You can just run 
$ sudo ./install_usb_rule.sh
(Needs root privileges for writing to /etc/)
