import pulumi
from pulumi import StackReference, export, ResourceOptions, Output
from datetime import datetime
import pytz
import json
import os
import platform
import pulumi_aws as aws
from common.autotag import register_auto_tags
from common.repositories import Repositories

"""
Grab Config
"""
config = pulumi.Config()

"""
Create Variables from pulumi config
"""
environment = pulumi.get_stack()

"""
Deployment Timestamp
"""
UTC = pytz.utc
datetime_utc = datetime.now(UTC)
deployment_timestamp = f"{datetime_utc.strftime('%Y-%m-%d %H:%M:%S %Z %z')}"

"""
Caller Identity Vars
"""
user_id = aws.get_caller_identity().user_id
account_id = aws.get_caller_identity().account_id

"""
Auto Tagging
"""
# Automagically applies the following tags to any resource created and managed by pulumi.
register_auto_tags({
    'managed_by_pulumi': 'true',
    'pulumi_project': pulumi.get_project(),
    'pulumi_stack': pulumi.get_stack(),
    'environment': environment,
    'deployment_timestamp_utc': deployment_timestamp,
    'deployed_by': os.getlogin(),
    'deployed_from': f"{platform.node()} - {platform.system()} {platform.release()}",
    'caller_identity_user_id': user_id,
    'caller_identity_account_id': account_id
})

"""
Create Repositories
"""
repositories = Repositories(account_id).create()