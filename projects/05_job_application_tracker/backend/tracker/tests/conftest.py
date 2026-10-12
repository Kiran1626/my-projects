import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    class _Defaults:
        format = "json"

    client = APIClient(enforce_csrf_checks=False)
    # APIClient defaults need the JSON content type set per request; patch the
    # generic _post to always send JSON so tests can pass None values freely.
    original_post = client.post

    def json_post(path, data=None, **kwargs):
        kwargs.setdefault("format", "json")
        return original_post(path, data, **kwargs)

    original_patch = client.patch

    def json_patch(path, data=None, **kwargs):
        kwargs.setdefault("format", "json")
        return original_patch(path, data, **kwargs)

    client.post = json_post
    client.patch = json_patch
    return client
