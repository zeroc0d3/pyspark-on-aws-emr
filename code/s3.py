import logging
import boto3
import os.path
import json
from botocore.exceptions import ClientError


def create_bucket(bucket_name, folders, logger):

    try:
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': s3_resource.meta.client.meta.region_name
            }
        )
        bucket.wait_until_exists()
        logger.info("Created bucket %s.", bucket_name)
    except ClientError:
        logger.exception("Couldn't create bucket %s.", bucket_name)
        raise


    try:
        for folder in folders:
            s3_resource.put_object(Bucket= bucket_name, Body='', Key=folder + '/')
            logger.info("Folder created %s.", f'{bucket_name}/{folder}')
    except ClientError:
        logger.exception("Couldn't create folder %s.", folder)
        raise    

    return bucket
    

def upload_to_bucket(bucket_name, f, folder, logger):
    
    try:
        s3_resource = boto3.client('s3')
        object_name = folder + "/{fname}".format(fname= os.path.basename(f)) 
        s3_resource.upload_file(f, bucket_name, object_name , ExtraArgs = None)
        logger.info(
            "Uploaded script %s to %s.", object_name,
            f'{bucket_name}/{folder}')
    except ClientError:
        logger.exception("Couldn't upload %s to %s.", object_name, bucket_name)
        raise


def put_object(bucket_name, jsd, folder, cluster_id,  logger):
    try:
        Key_name= f'{folder}/{cluster_id}_{folder}.json'
        s3_resource = boto3.client('s3')
        s3_resource.put_object(Bucket= bucket_name,  
                               Body=(bytes(json.dumps(jsd).encode('UTF-8'))), 
                               Key= Key_name)

        logger.info(
            "Uploaded file %s to %s.", Key_name, f'{bucket_name}/{folder}')
    except ClientError:
        logger.exception("Couldn't create folder %s.", folder)
        raise    


def delete_bucket(bucket, logger):

    try:        
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket(bucket)
        bucket.objects.delete()
        bucket.delete()
        logger.info("Emptied and removed bucket %s.", bucket)
    except ClientError:
        logger.exception("Couldn't remove bucket %s.", bucket)
        raise
