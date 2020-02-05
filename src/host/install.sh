#!/bin/bash

echo "Removing unnecessary data from binary folders.."
./clean_up_pyinstaller.sh

echo "Creating dir ~/.snopf.."
mkdir -p ~/.snopf/snopf_cmd
mkdir -p ~/.snopf/snopf_manager

echo "Copying data to ~/.snopf.."
cp -rf dist/pc/snopf_cmd ~/.snopf
cp -rf dist/pc/snopf_manager ~/.snopf
# cp dist/pc/snopf_password_request ~/.snopf

echo "Creating links in ~/.local/bin.."
cp -f snopf_cmd ~/.local/bin/
cp -f snopf_manager ~/.local/bin/
# ln -s ~/.snopf/snopf_password_request ~/.local/bin/snopf_password_request

echo "snopf is now installed to ~/.snopf."
echo "Run snopf_manager by typing snopf_manager into the command line."
echo "Run snopf_cmd by typing snopf_cmd into the command line."
