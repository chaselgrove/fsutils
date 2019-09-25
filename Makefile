default : build

PACKAGE_FILES = dist/fsutils-0.6.0.tar.gz \
                dist/fsutils-0.6.0-py2-none-any.whl

build : $(PACKAGE_FILES)

dist/fsutils-0.6.0.tar.gz : 
	python setup.py sdist

dist/fsutils-0.6.0-py2-none-any.whl : 
	python setup.py bdist_wheel

register : 
	python setup.py register

upload : $(PACKAGE_FILES)
	python -m twine upload $^

check : 
	python setup.py check

clean : 
	rm -f MANIFEST fsutils/*.pyc

clobber : clean
	rm -rf dist

# eof
