import os

from moto import mock_aws


@mock_aws
def test_launch():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

    import importlib

    from app import ec2_manager

    importlib.reload(ec2_manager)

    result = ec2_manager.launch_ec2_instances(1)
    assert result["status"] == "launching"
    assert len(result["instance_ids"]) == 1
