default : build

build : dist/fsutils-0.3.1.tar.gz

dist/fsutils-0.3.1.tar.gz : 
	python setup.py sdist

register : 
	python setup.py register

upload : 
	python setup.py sdist upload

check : 
	python setup.py check

clean : 
	rm -f MANIFEST fsutils/*.pyc

clobber : clean
	rm -rf dist

# eof
