sync:
	uv lock && uv sync --frozen

publish-test:
	uv publish --index=testpypi --trusted-publishing=always -v

publish:
	uv publish --index=pypi --trusted-publishing=always -v

build:
	uv build -o dist/

lint:
	uvx ruff check --fix --unsafe-fixes -e && ruff format