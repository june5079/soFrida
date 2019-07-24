import boto3, traceback, json
import subprocess
from botocore.exceptions import ClientError
from sflogger import sfLogger
from termcolor import cprint

class awsTester:
    def __init__(self, pkgid, accesskey, secretkey, stoken, awsservice, region, logger=""):
        self.pkgid = pkgid
        self.accesskey = accesskey
        self.secretkey = secretkey
        self.stoken = stoken
        self.awsservice = awsservice
        self.region = region
        self.logger = logger
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

    def message_send(self, data):
        if self.logger != "":
            self.logger.info(json.dumps(data))

    def s3_check(self, bucket, command):
        s3 = boto3.resource(
            's3',
            aws_access_key_id=self.accesskey,
            aws_secret_access_key=self.secretkey,
            aws_session_token=self.stoken,
            region_name=self.region
        )
        if command == 'ls':
            self.message_send({"service":"s3", "type":"start", "msg":"[*] S3 Service Check Start"})
            try:
                res = s3.Bucket(bucket)
                if res:
                    result = res.meta.client.list_objects(Bucket=bucket, Delimiter='/')
                    for o in result.get('CommonPrefixes'):
                        cprint(o.get('Prefix'), 'blue')
                        self.message_send({"service":"s3", "type":"list", "msg":o.get('Prefix')})
                    cprint ("[!] This Cloud-Backend is vulnerable", 'blue')
                    self.message_send({"service":"s3", "type":"vuln", "msg":"[!] This Cloud-Backend is vulnerable"})
                                        
            except ClientError as e:
                print (e)
                cprint ("[!] This Cloud-Backend is not vulnerable", 'blue')
                self.message_send({"service":"s3", "type":"novuln", "msg":"[!] This Cloud-Backend is not vulnerable"})

    def kinesis_check(self, command):
        client = self.client
        if command == 'list_streams':
            self.message_send({"service":"kinesis", "type":"start", "msg":"[*] Kinesis Service Check Start"})
            try:
                if client.list_streams() :
                    cprint ("[!] This Cloud-Backend is vulnerable", 'blue')
                    self.message_send({"service":"kinesis", "type":"vuln", "msg":"[!] This Cloud-Backend is vulnerable"})
                    cprint (client.list_streams(),'blue')
                    self.message_send({"service":"kinesis", "type":"list_streams", "msg":client.list_streams()})

            except ClientError as e:
                print (e)
                cprint ("[!] This Cloud-Backend is not vulnerable", 'blue')
                self.message_send({"service":"kinesis", "type":"novuln", "msg":"[!] This Cloud-Backend is not vulnerable"})
    
    def firehose_check(self, command):
        client = self.client
        if command == 'list_delivery_streams':
            self.message_send({"service":"firehose", "type":"start", "msg":"[*] Firehose Service Check Start"})
            try:
                res = client.list_delivery_streams()
                if res :
                    cprint ("[!] This Cloud-Backend is vulnerable", 'blue')
                    self.message_send({"service":"firehose", "type":"vuln", "msg":"[!] This Cloud-Backend is vulnerable"})
                    cprint (res,'blue')
                    self.message_send({"service":"firehose", "type":"list_delivery_streams", "msg":res})

            except ClientError as e:
                print (e)
                cprint ("[!] This Cloud-Backend is not vulnerable", 'blue')
                self.message_send({"service":"firehose", "type":"novuln", "msg":"[!] This Cloud-Backend is not vulnerable"})
