import boto3

class awsTester:
    def __init__(self, accesskey, secretkey, stoken, awsservice, region):
        self.accesskey = accesskey
        self.secretkey = secretkey
        self.stoken = stoken
        self.awsservice = awsservice
        self.region = region

    def s3check(self, bucket):
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(bucket)
        for obj in bucket.objects.all():
            print(obj.key)