import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:325125394024:DeployPortfolioTopic')
    try:
        s3 = boto3.resource('s3',config=Config(signature_version='s3v4'))


        portfolio_bucket = s3.Bucket('portfolio.moathmalkawi.info')
        build_bucket = s3.Bucket('portfoliobuild.moathmalkawi.info')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('Portfolio.zip',portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

                topic.publish(Subject="Portfolio Deployed",Message="Portfolio deployed successfully!")
                print "Job done!"
    except:
        topic.publish(Subject="Portfolio deploy Failed ", Message="The portfolio was not deployed successfully !")
        raise
    return 'Hello from Lambda'
