import os
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

import boto3
from moto import mock_ec2
from app.ec2_manager import launch_ec2_instances

@mock_ec2
def test_launch():
    result = launch_ec2_instances(1)
    assert result["status"] == "launching"
    assert len(result["instance_ids"]) == 1
    print("✅ EC2 mock test passed")

if __name__ == "__main__":
    test_launch()