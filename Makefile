format:
	black . -l 79
test:
	pytest tests
install:
	pip install git+https://github.com/ubicenter/openfisca-us
	pip install -e .
