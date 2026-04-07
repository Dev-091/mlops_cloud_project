import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
ec2 = boto3.client("ec2", region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

def launch_ec2_instances(count: int):
    image_id = os.getenv("EC2_IMAGE_ID", "ami-0c55b159cbfafe1f0")
    instance_type = os.getenv("EC2_INSTANCE_TYPE", "t2.micro")
    auto_stop_min = int(os.getenv("AUTO_TERMINATE_MINUTES", "30"))

    # UserData script to auto-shutdown
    user_data = f"""#!/bin/bash
echo "Instance launched for finger-count project" > /tmp/launched.txt
sleep {auto_stop_min * 60}
sudo shutdown -h now
"""

    try:
        # Dry-run first (validates permissions & quotas)
        ec2.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            MinCount=count,
            MaxCount=count,
            UserData=user_data,
            DryRun=True
        )
        print("✅ Dry-run passed. Proceeding to launch.")
    except ClientError as e:
        if "DryRunOperation" in str(e):
            print("✅ Dry-run successful. Launching real instances...")
        else:
            raise e

    # Real launch
    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType=instance_type,
        MinCount=count,
        MaxCount=count,
        UserData=user_data
    )

    instance_ids = [i["InstanceId"] for i in response["Instances"]]
    return {
        "status": "launching",
        "count": count,
        "instance_ids": instance_ids,
        "auto_terminate_minutes": auto_stop_min
    }