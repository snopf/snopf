# TODO chrome packaging

dist_path = ../dist/browser_extension/
work_path = ../build/

all_deps = $(wildcard icon/*.png)
all_deps += $(wildcard js/*.js)
all_deps += $(wildcard html/*.html)
all_deps += $(wildcard css/*.css)

firefox_deps = manifest_firefox.json
chrome_deps = manifest_chrome.json

excludes = Makefile manifest_firefox.json manifest_chrome.json

firefox:	$(dist_path)firefox/firefox.zip
	
$(dist_path)firefox/firefox.zip:	$(all_deps)	$(firefox_deps)
	mkdir -p $(dist_path)firefox
	cp manifest_firefox.json manifest.json
	cp com.snopf.snopf_firefox.json	$(dist_path)firefox/com.snopf.snopf.json
	zip -r -FS $@ * -x $(excludes)
