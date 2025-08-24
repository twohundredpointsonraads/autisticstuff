include .env

install:
	uv install

sync:
	uv lock && uv sync

publish-test:
	uv publish --index=testpypi --trusted-publishing=always

publish:
	uv publish --index=pypi --trusted-publishing=always

build:
	uv build -o dist/