format:
	black . -l 79
test:
	pytest tests -vv
install:
	pip install git+https://github.com/nikhilwoodruff/openfisca-us
	pip install -e .
