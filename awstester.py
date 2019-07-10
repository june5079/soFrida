import boto3, traceback, json
from botocore.exceptions import ClientError
from sflogger import sfLogger


class awsTester:
    def __init__(self, pkgid, accesskey, secretkey, stoken, awsservice, region):
        self.pkgid = pkgid
        self.accesskey = accesskey
        self.secretkey = secretkey
        self.stoken = stoken
        self.awsservice = awsservice
        self.region = region

    def s3_check(self, bucket, command):
        s3 = boto3.resource('s3')
        s3bucket = s3.Bucket(bucket)
        if command == 'ls':
            try:
                if (s3bucket.objects):
                    print ("This is vulnerable")
                    
            except ClientError as e:
                print (e)

    def kinesis_check(self, command):
        kinesis = boto3.client('kinesis')
        if command == 'list_streams':
            try:
                if kinesis.list_streams() :
                    print ("This is vulnerable")

            except ClientError as e:
                print ("This is not vulnerable")
    
    def firehose_check(self, command):
        firehose = boto3.client('firehose')
        if command == 'list_delivery_streams':
            try:
                res = firehose.list_delivery_streams()
                if res :
                    print ("This is vulnerable")
                    print (res)

            except ClientError as e:
                print ("This is not vulnerable")
