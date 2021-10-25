format:
	autopep8 . -r -i
	black . -l 79
test:
	pytest tests -vv
install:
	pip install git+https://github.com/PolicyEngine/openfisca-us
	pip install -e .[dev]
