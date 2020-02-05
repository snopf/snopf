#!/bin/bash

echo "Creating directory ~/.snopf/snopf_browser_driver"
mkdir -p ~/.snopf/snopf_browser_driver

echo "Copying browser driver to ~/.snopf"
cp -r dist/pc/snopf_browser_driver ~/.snopf

./create_snopf_native_manifest.py
mkdir -p ~/.mozilla/native-messaging-hosts/
cp dist/browser_extension/firefox/com.snopf.snopf.json ~/.mozilla/native-messaging-hosts/
echo "Done."
echo "You can now install the browser extension."
