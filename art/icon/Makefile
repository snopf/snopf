icon = icon.svg

sizes = 16 32 48 64 72 96 128 144 192 256 512
pngs = $(addsuffix .png, $(addprefix icon_png/icon_, $(sizes)))

all:	$(pngs) ico_file

$(pngs): $(icon)
	inkscape -z -f $(icon) -e $@ -w $(subst .png,,$(subst icon_png/icon_,,$@))
	
ico_file:	$(icon)
	convert -background transparent icon.svg -define icon:auto-resize=16,32,48,64,256 snopf.ico

clean:
	rm -rf *.png
