import pulumi
import pulumi_aws as aws
from datetime import datetime
import pytz
import json
from common.helpers import Helpers

"""
Grab Config
"""
config = pulumi.Config()

class Repositories():
    def __init__(self, account_id):
        self.account_id = account_id
        
    def get_repositories(self):
        repositories = config.require_object("repositories")
        return repositories
    
    def get_repo_config_value(self, repository, key: str, separator: str='.'):
        config = self.get_repositories().get(repository)
        key_value = Helpers.key_in_dict(config, key, separator)
        return key_value
    
    def generate_registry_policy_json(self, repository):
        # Create an empty list to append principals for policy
        principals = []
        
        # Append the root account of the current caller_identity.
        principals.append(f"arn:aws:iam::{self.account_id}:root")
        
        # Grab any additional principals from the stacks config.
        additional_principals = self.get_repo_config_value(repository, "policy.principals")
        
        # If the additional principals list is not equal to none then merge with the principals list.
        if additional_principals != "None":
            principals.extend(additional_principals)
        
        actions = self.get_repo_config_value(repository, "policy.actions")
        
        policy = json.dumps(
            {
                "Version": "2008-10-17",
                "Statement": [{
                    "Sid": "Allow ECR Access",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": principals
                    },
                    "Action": actions
                }]
            }            
        )
        
        return policy
    
    def generate_lifecycle_policy_json(self, repository):
        untagged_retention_days = self.get_repo_config_value(repository, "untagged_retention_days")
        taggeed_image_count_to_keep = self.get_repo_config_value(repository, "tagged_image_count_to_keep")
        tag_prefix_list = self.get_repo_config_value(repository, "tag_prefix_list")
        
        policy = json.dumps(
            {
                "rules": [
                    {
                        "rulePriority": 1,
                        "description":  f"Expire untagged images older than {untagged_retention_days} day(s)",
                        "selection": {
                            "tagStatus": "untagged",
                            "countType": "sinceImagePushed",
                            "countUnit": "days",
                            "countNumber": untagged_retention_days
                        },
                        "action": {
                            "type": "expire"
                        }
                    },
                    {
                        "rulePriority": 2,
                        "description": f"Keep last {taggeed_image_count_to_keep} images",
                        "selection": {
                            "tagStatus": "tagged",
                            "tagPrefixList": tag_prefix_list,
                            "countType": "imageCountMoreThan",
                            "countNumber": taggeed_image_count_to_keep
                        },
                        "action": {
                            "type": "expire"
                        }
                    }
                ]
            }
        )
        
        print(policy)
        
        return policy
        
    def create(self):
        
        # Get all of the repositories from the config.
        repositories = self.get_repositories()

        for repo_name in repositories:
            
            """
            Create ECR Repo
            """
            repository = aws.ecr.Repository(
                repo_name,
                name = repo_name,
                image_scanning_configuration = aws.ecr.RepositoryImageScanningConfigurationArgs(scan_on_push=self.get_repo_config_value(repo_name, "scan_on_push")),
                image_tag_mutability = self.get_repo_config_value(repo_name, "image_tag_mutability")
            )
            
            """
            ECR Policy (Permissions)
            """
            ecr_registry_policy = aws.ecr.RepositoryPolicy(
                f"{repo_name}-reg-pol",
                repository = repo_name,
                policy = self.generate_registry_policy_json(repo_name),
                opts = pulumi.ResourceOptions(parent = repository, depends_on=[repository])
            )

            """
            Lifecycle Policies
            """
            lifecycle_policy = aws.ecr.LifecyclePolicy(
                f"{repo_name}-lc-pol",
                repository = repository.name,
                policy = self.generate_lifecycle_policy_json(repo_name),
                opts = pulumi.ResourceOptions(parent = repository, depends_on=[repository])
            )