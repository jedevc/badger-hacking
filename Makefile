.PHONY: all
all: dist

.PHONY: dist
dist: pre-dist dist/main.py dist/badger_os.py dist/badge.txt dist/lemon.raw

.PHONY: deploy
deploy: dist
	sh -c "find ./dist/ -mindepth 1 -type d -printf '%P\0' | xargs -0 -I %% ../micropython/tools/pyboard.py -f mkdir %%"
	sh -c "find ./dist/ -mindepth 1 -type f -printf '%P\0' | xargs -0 -I %% ../micropython/tools/pyboard.py -f cp dist/%% :%%"

dist/%.py: src/%.py
	cp $< $@

dist/%.txt: res/%.txt
	cp $< $@

dist/%.raw: res/%.png
	python3 tools/convert.py --binary --out $@ $<

.PHONY: pre-dist
pre-dist:
	mkdir -p dist/
	
.PHONY: clean
clean:
	rm -rf dist/
