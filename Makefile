format:
	black . -l 79
test:
	pytest tests
install:
	pip install -e .
	pip install git+https://github.com/ubicenter/openfisca-us
