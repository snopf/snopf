icon = icon.svg

sizes = 16 32 48 64 72 96 128 144 192 256 512
pngs = $(addsuffix .png, $(addprefix icon_png/icon_, $(sizes)))

all:	$(pngs)

$(pngs): $(icon)
	inkscape -z -f $(icon) -e $@ -w $(subst .png,,$(subst icon_png/icon_,,$@))

clean:
	rm -rf *.png
