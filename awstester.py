import boto3, traceback, json
import subprocess
from botocore.exceptions import ClientError
from sflogger import sfLogger
from termcolor import cprint

class awsTester:
    def __init__(self, pkgid, accesskey, secretkey, stoken, awsservice, region):
        self.pkgid = pkgid
        self.accesskey = accesskey
        self.secretkey = secretkey
        self.stoken = stoken
        self.awsservice = awsservice
        self.region = region
        self.client = boto3.client(
            awsservice,
            aws_access_key_id=self.accesskey,
            aws_secret_access_key=self.secretkey,
            aws_session_token=self.stoken,
            region_name=self.region
        )

    def manual_check(self, command):
        subprocess.call("aws configure set aws_access_key_id %s"%self.accesskey, shell=True)
        subprocess.call("aws configure set aws_secret_access_key %s"%self.secretkey, shell=True)
        if self.stoken != None:
            subprocess.call("aws configure set aws_session_token %s"%self.stoken, shell=True)
        subprocess.call("aws configure set region %s"%self.region, shell=True)

        # cmd is from user input : ex) "aws s3 ls s3://bucketname"
        cmd = command
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        while res.poll() is None:
            l = res.stdout.readline() # This blocks until it receives a newline.
            cprint (l, 'blue')

    def s3_check(self, bucket, command):
        s3 = boto3.resource(
            's3',
            aws_access_key_id=self.accesskey,
            aws_secret_access_key=self.secretkey,
            aws_session_token=self.stoken,
            region_name=self.region
        )
        if command == 'ls':
            try:
                res = s3.Bucket(bucket)
                if res:
                    result = res.meta.client.list_objects(Bucket=bucket, Delimiter='/')
                    for o in result.get('CommonPrefixes'):
                        cprint(o.get('Prefix'), 'blue')
                    cprint ("[!] This Cloud-Backend is vulnerable", 'blue')
                                        
            except ClientError as e:
                print (e)
                cprint ("[!] This Cloud-Backend is not vulnerable", 'blue')

    def kinesis_check(self, command):
        client = self.client
        if command == 'list_streams':
            try:
                if client.list_streams() :
                    cprint ("[!] This Cloud-Backend is vulnerable", 'blue')
                    cprint (client.list_streams(),'blue')

            except ClientError as e:
                print (e)
                cprint ("[!] This Cloud-Backend is not vulnerable", 'blue')
    
    def firehose_check(self, command):
        client = self.client
        if command == 'list_delivery_streams':
            try:
                res = client.list_delivery_streams()
                if res :
                    cprint ("[!] This Cloud-Backend is vulnerable", 'blue')
                    cprint (res,'blue')

            except ClientError as e:
                print (e)
                cprint ("[!] This Cloud-Backend is not vulnerable", 'blue')
