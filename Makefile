default : build

build : dist/fsutils-0.1.2.tar.gz

dist/fsutils-0.1.2.tar.gz : 
	python setup.py sdist

register : 
	python setup.py register

upload : 
	python setup.py sdist upload

check : 
	python setup.py check

clean : 
	rm -f MANIFEST

clobber : clean
	rm -rf dist

# eof
