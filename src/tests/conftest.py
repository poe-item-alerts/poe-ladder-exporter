import os

import boto3
import pytest

from botocore.exceptions import ClientError
from moto import (
    mock_ssm,
    mock_sts,
    mock_lambda,
    mock_iam,
    mock_stepfunctions
)


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


@pytest.fixture
def ssm_mock(aws_credentials):
    with mock_ssm():
        yield boto3.client("ssm", region_name="eu-central-1")


@pytest.fixture
def sts_mock(aws_credentials):
    with mock_sts():
        yield boto3.client("sts", region_name="eu-central-1")


@pytest.fixture
def lambda_mock(aws_credentials):
    with mock_lambda():
        yield boto3.client("lambda", region_name="eu-central-1")


@pytest.fixture
def iam_mock(aws_credentials):
    with mock_iam():
        yield boto3.client("iam", region_name="eu-central-1")


@pytest.fixture
def sfn_mock(aws_credentials):
    with mock_stepfunctions():
        yield boto3.client("stepfunctions", region_name="eu-central-1")


@pytest.fixture
def iam_role(iam_mock):
    try:
        return iam_mock.get_role(RoleName="my-role")["Role"]["Arn"]
    except ClientError:
        return iam_mock.create_role(
            RoleName="my-role",
            AssumeRolePolicyDocument="some policy",
            Path="/my-path/",
        )["Role"]["Arn"]
