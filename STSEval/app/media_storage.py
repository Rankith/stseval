from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class MediaStorage(S3Boto3Storage):
    bucket_name = settings.AWS_MEDIA_BUCKET_NAME
    access_key = settings.AWS_MEDIA_ID
    secret_key = settings.AWS_MEDIA_SECRET
    region_name = settings.AWS_MEDIA_REGION_NAME
    custom_domain = settings.AWS_MEDIA_CUSTOM_DOMAIN
    default_acl = 'public-read'