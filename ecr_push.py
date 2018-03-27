#!/usr/bin/env python

import re, docker, argparse, boto3, base64


def main():
  p = argparse.ArgumentParser(description="Ecr Push")
  p.add_argument('--tag', required=True)
  p.add_argument('--name', required=True)
  p.add_argument('--account', required=True)
  p.add_argument('--regions', nargs='+', required=True)
  p.add_argument('--role-arn', required=True)
  p.add_argument('--access-key-id', required=True)
  p.add_argument('--secret-access-key', required=True)

  args = p.parse_args()

  ecr_push(
    args.name, args.tag,
    args.account, args.regions, args.access_key_id,
    args.secret_access_key, args.role_arn
  )

def ecr_push(name, tag, account, regions, access_key_id, secret_access_key, role_arn):
  for region in regions:

    client = ecr_login(region, access_key_id, secret_access_key, account, role_arn)

    source = "%s:%s" % (name, tag)
    # 878759797472.dkr.ecr.us-east-2.amazonaws.com
    repo = "%s.dkr.ecr.%s.amazonaws.com" % (account, region)
    target = "%s/%s" % (repo, name)

    print "tagging result %s" % (client.tag(source, target, tag))

    print "pushing %s:%s" % (target, tag)
    for line in client.push(target, tag=tag, stream=True):
      print line

def ecr_login(region, access_key_id, secret_access_key, account, role_arn):
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

  client = docker.APIClient(base_url='unix://var/run/docker.sock')
  client.login(username='AWS', password=password, registry=endpoint)

  return client

if __name__ == '__main__':
  main()
