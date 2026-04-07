# find_ami.py
import boto3
import os
from dotenv import load_dotenv

load_dotenv()
region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

ec2 = boto3.client("ec2", region_name=region)

print(f"Searching for latest Amazon Linux 2023 AMI in {region}...")
response = ec2.describe_images(
    Owners=["amazon"],
    Filters=[
        {"Name": "name", "Values": ["al2023-ami-2023.*-x86_64"]},
        {"Name": "state", "Values": ["available"]},
        {"Name": "architecture", "Values": ["x86_64"]},
        {"Name": "root-device-type", "Values": ["ebs"]},
        {"Name": "virtualization-type", "Values": ["hvm"]},
    ],
)

# Sort by creation date & pick newest
images = sorted(response["Images"], key=lambda x: x["CreationDate"], reverse=True)
if images:
    latest_ami = images[0]["ImageId"]
    print(f"Found: {latest_ami}")
    print(f"Copy this into your .env -> EC2_IMAGE_ID={latest_ami}")
else:
    print("No Amazon Linux 2023 AMI found in this region.")
    print("Try changing AWS_DEFAULT_REGION=us-east-1 in .env")