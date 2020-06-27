all:	test snopf

dist_path = ../dist/pc/
work_path = ../build

snopf:	gui $(wildcard *.py)
	bash insert_git_commit.sh
	pyinstaller snopf_manager.py --distpath=$(dist_path) --workpath=$(work_path)/snopf_manager --specpath=$(work_path) --paths=. --name=snopf --noconfirm
	mv __get_commit_hash___ get_commit_hash.py
	bash clean_up_pyinstaller.sh

test:	
	pytest

pyui = $(addprefix ui_, $(patsubst %.ui,%.py,$(wildcard *.ui)))

gui:	$(pyui) resources_rc.py
	
ui_%.py:	%.ui
	pyside2-uic $^ -o $@ 

resources_rc.py:	resources.qrc
	pyside2-rcc resources.qrc > resources_rc.py
	
clean:
	rm -rf ../build
	rm -rf ../dist
