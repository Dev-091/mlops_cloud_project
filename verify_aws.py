# verify_aws.py
import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

def test_aws_connection():
    print("🔍 Testing AWS Credentials & Permissions...")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    image_id = os.getenv("EC2_IMAGE_ID", "ami-0c55b159cbfafe1f0")
    instance_type = os.getenv("EC2_INSTANCE_TYPE", "t2.micro")

    try:
        ec2 = boto3.client("ec2", region_name=region)
        
        # ✅ Dry-run tests IAM permissions, AMI validity, instance type, & quotas
        print("🛡️ Running dry-run EC2 launch validation...")
        ec2.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            DryRun=True
        )
        print("❌ Dry-run should have raised 'DryRunOperation' but didn't.")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == "DryRunOperation":
            print("✅ Dry-run passed! Your keys have correct EC2 permissions.")
            print("🔒 Safe to proceed. No instances were launched.")
        else:
            print(f"❌ Permission/Config Error: {error_code}")
            print(f"💡 Message: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_aws_connection()