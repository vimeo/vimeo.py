import pytest

def pytest_addoption(parser):
    parser.addoption("--dev", action="store_true",
            help="Run against a local development server at http://vimeo.dev")

@pytest.fixture
def dev(request):
    return request.config.getoption("--dev")

