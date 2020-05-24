import io
import json
import os
import zipfile

import pytest

from botocore.stub import Stubber
from moto import mock_lambda

import poe_ladder_exporter.ladder
from poe_ladder_exporter.handler import handler


def ladder_response(ladder_name):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.join(
        this_dir,
        "resources",
        "ladder_api_response.json"
    )
    with open(test_path) as f:
        ladder_response = json.load(f)
    return ladder_response["entries"]


def empty_ladder_response(ladder_name):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.join(
        this_dir,
        "resources",
        "empty_ladder_api_response.json"
    )
    with open(test_path) as f:
        ladder_response = json.load(f)
    return ladder_response["entries"]
    

@pytest.fixture
def ladder_export_patched(monkeypatch):
    monkeypatch.setattr(poe_ladder_exporter.handler, "ladder_export", ladder_response)


@pytest.fixture
def ladder_export_empty_patched(monkeypatch):
    monkeypatch.setattr(poe_ladder_exporter.handler, "ladder_export", empty_ladder_response)


@pytest.fixture
def gravedigger_lambda(lambda_mock, iam_role):
    pfunc = """
def lambda_handler(event, context):
    print("custom log event")
    return event
""" 
    zip_output = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_output, "w", zipfile.ZIP_DEFLATED)
    zip_file.writestr("lambda_function.py", pfunc)
    zip_file.close()
    zip_output.seek(0)
    lambda_zip = zip_output.read()
     
    lambda_mock.create_function(
        FunctionName="poe_gravedigger",
        Runtime="python3.7",
        Role=iam_role,
        Handler="lambda_function.lambda_handler",
        Code={"ZipFile": lambda_zip},
        Description="test lambda function",
        Timeout=3,
        MemorySize=128,
        Publish=True,
    )


@pytest.fixture
def character_export_sfn(sfn_mock, iam_role):
    simple_definition = (
        '{"Comment": "An example of the Amazon States Language using a choice state.",'
        '"StartAt": "DefaultState",'
        '"States": '
        '{"DefaultState": {"Type": "Fail","Error": "DefaultStateError","Cause": "No Matches!"}}}'
    )
    sfn_mock.create_state_machine(
        name="poe_character_exporter",
        definition=str(simple_definition),
        roleArn=iam_role
    )


@pytest.fixture
def ssm_ladder(ssm_mock):
    ssm_mock.put_parameter(
        Name="/poe-item-alerts/character-load/ladders",
        Value="test",
        Type="String"
    )


@pytest.fixture
def aws_environment(ssm_mock, sfn_mock, ssm_ladder, gravedigger_lambda, character_export_sfn):
    pass

def test_handler_happy_path(caplog, aws_environment, ladder_export_patched):
    test_event = {}
    handler(test_event, None)
    assert "Got ladder with 9 entries" in caplog.text
    assert "Step function triggered successfully" in caplog.text


def test_handler_empty_ladder(caplog, aws_environment, ladder_export_empty_patched):
    test_event = {"key": "value"}
    handler(test_event, None)
    print(caplog.text)
    assert "Got ladder with 0 entries" in caplog.text
    assert "Ladder is empty, has the event started?" in caplog.text


def test_handler_sfn_execution_limit(caplog, aws_environment, sfn_mock, ladder_export_patched):
    stubber = Stubber(sfn_mock)
    stubber.add_response("list_state_machines",)
    stubber.add_client_error(
        "start_execution",
        "ExecutionLimitExceeded"
    )
    print(type(sfn_mock))
    print(stubber)
    with stubber:
        state_machines = sfn_mock.list_state_machines()["stateMachines"]
        state_machine = [s["stateMachineArn"] for s in state_machines if s["name"] == "poe_character_exporter"][0]
        response = sfn_mock.start_execution(
            # stateMachineArn="arn:aws:states:eu-central-1:983498139013:stateMachine:poe_character_exporter",
            stateMachineArn=state_machine,
            name="test",
            input="test"
        )
        print(response)
    assert True == False
    # handler(test_event, None)


# @patch("poe_ladder_exporter.ladder.requests.get")
# def test_ladder_export_200(self, mock_get):
#     this_dir = os.path.dirname(os.path.abspath(__file__))
#     test_path = os.path.join(
#         this_dir,
#         "resources",
#         "ladder_api_response.json"
#     )
#     mock_get.return_value.status_code = 200
#     with open(test_path) as f:
#         ladder_response = json.load(f)
#     mock_get.return_value.json.return_value = ladder_response
#     response = ladder_export("test_ladder")
#     assert response == ladder_response

# @patch("poe_ladder_exporter.ladder.requests.get")
# def test_ladder_export_404(self, mock_get):
#     mock_get.return_value.status_code = 404
#     response = ladder_export("test_ladder")
#     assert response == {}

# @patch("poe_ladder_exporter.ladder.requests.get")
# def test_ladder_export_unhandled(self, mock_get):
#     mock_get.return_value.status_code = 401
#     response = ladder_export("test_ladder")
#     assert response == {}

# def test_rate_limit_no_violation(self):
#     test_headers = {
#         "X-Rate-Limit-Ip": "45:60:60,240:240:900",
#         "X-Rate-Limit-Ip-State": "1:60:0,1:240:0"
#     }
#     _rate_limit_backoff(test_headers)

# @patch("poe_ladder_exporter.ladder.time.sleep")
# def test_rate_limit_violation(self, sleep_mock):
#     test_headers = {
#         "X-Rate-Limit-Ip": "45:60:60,240:240:900",
#         "X-Rate-Limit-Ip-State": "44:60:0,44:240:0"
#     }
#     _rate_limit_backoff(test_headers)
#     sleep_mock.assert_called_once()

