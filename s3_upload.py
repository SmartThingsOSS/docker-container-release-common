#!/usr/bin/env python

import re, argparse, boto3


def main():
  p = argparse.ArgumentParser(description="Ecr Push")
  p.add_argument('--version', required=True)
  p.add_argument('--team', required=True)
  p.add_argument('--app', required=True)
  p.add_argument('--bucket', required=True)
  p.add_argument('--files', nargs='+', required=True)
  p.add_argument('--role-arn', required=True)
  p.add_argument('--access-key-id', required=False)
  p.add_argument('--secret-access-key', required=False)

  args = p.parse_args()

  upload(
    args.bucket, 
    args.team,
    args.app,
    args.version,
    args.files,
    args.role_arn, 
    args.access_key_id, 
    args.secret_access_key
  )

def login(access_key_id, secret_access_key, role_arn):
  sts = boto3.client('sts',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key
  )

  assumed = sts.assume_role(
    RoleArn=role_arn,
    RoleSessionName="AssumedRoleSession1"
  )

  creds = assumed['Credentials']

  return boto3.client('s3',
    aws_access_key_id=creds['AccessKeyId'],
    aws_secret_access_key=creds['SecretAccessKey'],
    aws_session_token=creds['SessionToken']
  )

def upload(bucket, team, app, version, files, role_arn, access_key_id, secret_access_key):
  s3 = login(access_key_id, secret_access_key, role_arn)
  for file in files:
    with open(file, 'r') as data:
      # config / $team / $app / $version / system / $file
      path = "config/%s/%s/%s/system/%s" % (team, app, version, file)
      s3.put_object(Bucket=bucket, Key=path, Body=data)

if __name__ == '__main__':
  main()
