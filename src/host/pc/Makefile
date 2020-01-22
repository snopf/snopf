deps_all = requests.py usb_comm.py
deps_cmd = snopf_cmd.py mnemonic.py password_generator.py
deps_browser_driver = native_app/snopf_browser_driver.py

deps_qt = $(wildcard qt/*.py)

dist_path = ../dist/pc/
work_path = ../build

cmd_path = $(dist_path)snopf_cmd/
manager_path = $(dist_path)snopf_manager/
driver_path = $(dist_path)snopf_browser_driver/

all:	test cmd snopf_manager browser_driver

cmd:			$(cmd_path)snopf_cmd
snopf_manager:		$(manager_path)snopf_manager
browser_driver:		$(driver_path)snopf_browser_driver

$(cmd_path)snopf_cmd:	$(deps_all) $(deps_cmd)
	pyinstaller snopf_cmd.py --distpath=$(dist_path) --workpath=$(work_path)/snopf_cmd --specpath=$(work_path) --name=snopf_cmd --add-data '../pc/wordlist/english.txt:wordlist/' --noconfirm
	git rev-parse HEAD > $(cmd_path)commit_hash.txt

$(manager_path)snopf_manager:	$(deps_all) $(deps_qt)
	pyinstaller qt/snopf_manager.py --distpath=$(dist_path) --workpath=$(work_path)/snopf_manager --specpath=$(work_path) --paths=. --name=snopf_manager --noconfirm
	git rev-parse HEAD > $(manager_path)commit_hash.txt
	
$(driver_path)snopf_browser_driver:	$(deps_all) $(deps_browser_driver)
	pyinstaller native_app/snopf_browser_driver.py --distpath=$(dist_path) --workpath=$(work_path)/snopf_browser_driver --specpath=$(work_path) --paths=. --name=snopf_browser_driver --noconfirm
	git rev-parse HEAD > $(driver_path)commit_hash.txt

test:	
	pytest

clean:
	rm -rf ../build
	rm -rf ../dist
