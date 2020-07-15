ifeq ($(OS), Windows_NT)
	TARGET = snopf_windows
	remove = powershell Remove-Item -Recurse -ErrorAction Ignore -Path
	pyinstall_upxdir = --upx-dir=./../../../3rdparty/upx
else
	TARGET = snopf_linux
	remove = rm -rf
endif

dist_path = ../dist/pc/
work_path = ../build
icon_path = ../../../art/icon/snopf.ico

PYINSTALL_CMD = pyinstaller snopf_manager.py --noconsole  --distpath=$(dist_path) --workpath=$(work_path)/snopf_manager --specpath=$(work_path) --paths=. --name=snopf --noconfirm --icon=$(icon_path) --onefile $(pyinstall_upxdir)

all:	test $(TARGET)

snopf_linux:	gui $(wildcard *.py)
	bash insert_git_commit.sh
	$(PYINSTALL_CMD)
	mv __get_commit_hash___ get_commit_hash.py

snopf_windows: gui $(wildcard *.py)
	powershell .\insert_git_commit.ps1
	powershell $(PYINSTALL_CMD)
	powershell rm .\get_commit_hash.py
	powershell Rename-Item -Path "__get_commit_hash___" -NewName "get_commit_hash.py"
	
test:	
	pytest

pyui = $(addprefix ui_, $(patsubst %.ui,%.py,$(wildcard *.ui)))

gui:	$(pyui) resources_rc.py
	
ui_%.py:	%.ui
	pyside2-uic $^ -o $@ 

resources_rc.py:	resources.qrc
	pyside2-rcc resources.qrc > resources_rc.py
	
clean:
	$(remove) ../build
	$(remove) ../dist
