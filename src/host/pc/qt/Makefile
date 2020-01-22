pyui = $(addprefix ui_, $(patsubst %.ui,%.py,$(wildcard *.ui)))

all:	gui resources.py

gui:	$(pyui) resources.py
	
ui_%.py:	%.ui
	pyside2-uic $^ -o $@ 

resources.py:	resources.qrc
	pyside2-rcc resources.qrc > resources.py
