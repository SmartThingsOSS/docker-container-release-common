#!/usr/bin/env python

import boto3, argparse, docker, base64

def main():
  p = argparse.ArgumentParser(description="Ecr Login")
  p.add_argument('--region', required=True)
  p.add_argument('--account', required=True)
  p.add_argument('--role-arn', required=True)
  p.add_argument('--access-key-id', required=True)
  p.add_argument('--secret-access-key', required=True)

  args = p.parse_args()


def ecr_login(account, region, access_key_id, secret_access_key, role_arn):
  sts = boto3.client('sts',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key
  )

  assumed = sts.assume_role(
    RoleArn=role_arn,
    RoleSessionName="AssumedRoleSession1"
  )

  creds = assumed['Credentials']

  ecr = boto3.client('ecr',
    region_name=region,
    aws_access_key_id=creds['AccessKeyId'],
    aws_secret_access_key=creds['SecretAccessKey'],
    aws_session_token=creds['SessionToken']
  )
  res = ecr.get_authorization_token(
    registryIds=[account]
  )

  auth = res["authorizationData"][0]
  token = auth["authorizationToken"]
  endpoint = auth["proxyEndpoint"]

  user, password = base64.b64decode(token).split(':')

  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.login(username='AWS', password=password, registry=endpoint)

  return client

if __name__ == '__main__':
  main()
