all:
	pep8 gog.py cli.py
	pylint -d E1103 gog.py cli.py
