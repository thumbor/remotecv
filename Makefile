setup:
	@pip install -e.\[tests\]

test:
	@pyvows -vv --profile --cover --cover-package=remotecv
