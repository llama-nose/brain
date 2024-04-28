import argparse
import json
import logging
import numpy as np
import os
import time
import pandas as pd

from utils.s3 import (
    list_files, download_file, read_and_combine_arrays,
    read_and_combine_arrays_in_batches
)
from utils.dynamo import (
    query_table
)

from brain.evaluator import Evaluator
from brain.generator import EmbeddingGenerator
from brain.visualizer import DataVisualizer

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):

    # Grab data from the event
    bucket = event['bucket']
    prefix = os.path.join(event['user_id'], event['session_id'])

    start = time.time()
    embeddings = read_and_combine_arrays(bucket, prefix)
    print(f"Reading and combining arrays in batches took {time.time() - start:.2f} seconds.")

    start = time.time()
    text = query_table(event['session_id'])
    print(f"Querying table took {time.time() - start:.2f} seconds.")
    # Process the text to make it make sense
    responses = [t['content'] for t in text]

    # print("WARNING - Using hardcoded path to embeddings.npy")
    # embeddings = np.load('data/embeddings.npy')
    # responses = np.load('data/responses.npy')

    # Initialize evaluator
    lln_evaluator = Evaluator(embeddings)
    lln_evaluator.fit()

    # Find the distance of each sample
    distances = []
    for idx in range(embeddings.shape[0]):
        sample = embeddings[idx]
        distance = lln_evaluator.evaluate(sample)
        distances.append(distance)


    # Make a pandas dataframe and show it
    data = {
        'text': responses,
        'distances': distances
    }

    # Return the message
    return {
        'statusCode': 200,
        'body': data
    }


def parse_args():
    parser = argparse.ArgumentParser(description='Llama Nose Brain Lambda Function.')
    parser.add_argument('--test', type=str, required=True, help='Path to test JSON.')
    return parser.parse_args()


if __name__ == '__main__':
    # Test the handler
    args = parse_args()

    # Load the test JSON
    with open(args.test, 'r') as f:
        event = json.load(f)

    context = None
    print(handler(event, context))