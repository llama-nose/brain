import boto3
import pickle
import numpy as np
from io import BytesIO

def download_file(bucket_name, key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, key, local_path)
    return

def list_files(bucket, prefix):

    s3 = boto3.client('s3')

    files = []
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            files.append(obj['Key'])

    return files


def read_and_combine_arrays(bucket, prefix):
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    arrays = []

    # Iterate through the objects in the specified prefix
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            # Get the object
            response = s3.get_object(Bucket=bucket, Key=obj['Key'])
            # Read the object's body into a numpy array
            body = response['Body'].read()
            # Deserialize the numpy array
            file_like_object = BytesIO(body)
            array = np.load(file_like_object)

            arrays.append(array)

    # Combine all arrays into a single numpy array
    return np.vstack(arrays)


def read_and_combine_arrays_in_batches(bucket, prefix, batch_size=10):
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    combined_arrays = None

    # Batch control variables
    current_batch = []
    batch_count = 0

    # Iterate through the objects in the specified prefix
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            # Get the object
            response = s3.get_object(Bucket=bucket, Key=obj['Key'])
            # Read the object's body into a numpy array
            body = response['Body'].read()
            # Convert bytes to a file-like object for np.load()
            file_like_object = BytesIO(body)
            array = np.load(file_like_object)
            current_batch.append(array)

            # Check if the current batch should be processed
            if len(current_batch) == batch_size:
                batch_arrays = np.vstack(current_batch)
                if combined_arrays is None:
                    combined_arrays = batch_arrays
                else:
                    combined_arrays = np.vstack((combined_arrays, batch_arrays))
                current_batch = []
                batch_count += 1
                print(f"Processed batch {batch_count}")

    # Process any remaining arrays in the last batch
    if current_batch:
        batch_arrays = np.vstack(current_batch)
        if combined_arrays is None:
            combined_arrays = batch_arrays
        else:
            combined_arrays = np.vstack((combined_arrays, batch_arrays))
        print(f"Processed final batch {batch_count + 1}")

    return combined_arrays