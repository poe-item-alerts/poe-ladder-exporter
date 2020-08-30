import json
import os

import pytest
from requests_mock import ANY as http_any

from poe_api import (_make_call, get_ladder)


this_dir = os.path.dirname(os.path.abspath(__file__))


def test_make_call_all(requests_mock):
    requests_mock.get(http_any)
    _make_call("ladder/TestLeague",
               parameters={"limit": 44, "offset": 0},
               headers={"content-type": "application/json"})
    assert requests_mock.called == True
    assert requests_mock.call_count == 1
    request = requests_mock.request_history[0]
    assert request.method == "GET"
    assert request.url == "https://api.pathofexile.com/ladder/TestLeague?limit=44&offset=0"
    assert "content-type" in request.headers
    assert request.headers["content-type"] == "application/json"
    

def test_make_call_no_params(requests_mock):
    requests_mock.get(http_any)
    _make_call("ladder/TestLeague", headers={"content-type": "application/json"})
    assert requests_mock.called == True
    assert requests_mock.call_count == 1
    request = requests_mock.request_history[0]
    assert request.method == "GET"
    assert request.url == "https://api.pathofexile.com/ladder/TestLeague"
    assert "content-type" in request.headers
    assert request.headers["content-type"] == "application/json"



def test_make_call_no_headers(requests_mock):
    requests_mock.get(http_any)
    _make_call("ladder/TestLeague", parameters={"limit": 44, "offset": 0})
    assert requests_mock.called == True
    assert requests_mock.call_count == 1
    request = requests_mock.request_history[0]
    assert request.method == "GET"
    assert request.url == "https://api.pathofexile.com/ladder/TestLeague?limit=44&offset=0"


def test_make_call_no_headers_no_params(requests_mock):
    requests_mock.get(http_any)
    _make_call("ladder/TestLeague")
    assert requests_mock.called == True
    assert requests_mock.call_count == 1
    request = requests_mock.request_history[0]
    assert request.method == "GET"
    assert request.url == "https://api.pathofexile.com/ladder/TestLeague"


def test_get_ladder_happy_path(requests_mock):
    ladder_response_path = os.path.join(
        this_dir,
        "poe_api_responses",
        "ladder_api_response.json"
    )
    with open(ladder_response_path) as f:
        ladder_response = json.load(f)
    requests_mock.get(http_any, json=ladder_response, status_code=200)
    result = get_ladder("TestLeague")
    assert result == ladder_response


def test_get_ladder_404(requests_mock):
    requests_mock.get(http_any, status_code=404)
    result = get_ladder("TestLeague")
    assert result == {}


def test_get_ladder_panic(requests_mock):
    requests_mock.get(http_any, status_code=302)
    with pytest.raises(SystemExit) as exit:
        get_ladder("TestLeague")
    assert str(exit.value) == "1"
