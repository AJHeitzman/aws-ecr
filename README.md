![Pulumi](https://img.shields.io/badge/Pulumi-3.88.0-informational?logo=Pulumi&logoColor=purple)
![Python](https://img.shields.io/badge/Python-3.11.6-informational?logo=Python&logoColor=yellow)
![AWS-CLI](https://img.shields.io/badge/AWS_CLI-2.13.5-informational?logo=Amazon&logoColor=orange)
![Visual_Studio_Code](https://img.shields.io/badge/Visual_Studio_Code-1.83.0-informational?logo=VisualStudioCode)

# AWS ECR
This is a [Pulumi](www.pulumi.com) Python project used to provision ECR in AWS.

## Multiple AWS Account Setup
This project will easily support a multiple AWS account deployment. Simply change aws profile in the stacks config to one that is configured to use the account you wish to deploy resources to.

```yaml
config:
  ...
  aws:profile: <aws_profile_name_here>
```
