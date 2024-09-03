.PHONY: default wheel dev convert-rst resize update-doc docs prepare-release release publish-no-test publish test
.ONESHELL:

PYTHON=`which python`
VERSION=`< VERSION`

author=$(Ge Yang)
author_email=$(ge.ike.yang@gmail.com)

# notes on python packaging: http://python-packaging.readthedocs.io/en/latest/minimal.html
default: publish release
wheel:
	rm -rf dist
	python setup.py bdist_wheel
dev:
	make wheel
	pip install --ignore-installed dist/neverwhere*.whl
convert-rst:
	pandoc -s README.md -o README --to=rst
	sed -i '' 's/code/code-block/g' README
	sed -i '' 's/\.\. code-block:: log/.. code-block:: text/g' README
	sed -i '' 's/\.\//https\:\/\/github\.com\/geyang\/neverwhere\/blob\/master\//g' README
	perl -p -i -e 's/\.(jpg|png|gif)/.$$1?raw=true/' README
	rst-lint README
dev-docs:
	sphinx-autobuild docs docs/_build/html
docs:
	rm -rf docs/_build
	cd docs && make html
	cd docs/_build/html && python -m http.server 8888
prepare:
	-git tag -d v$(VERSION)
	-git tag -d latest
release: prepare
	git push
	git tag v$(VERSION) -m '$(msg)'
	git tag latest
	git push origin --tags -f
publish: convert-rst
	make wheel
	twine upload dist/*
test:
	python -m pytest tests --capture=no
