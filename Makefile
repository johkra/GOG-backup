all:
	pep8 gog.py
	pylint -d E1103 gog.py
