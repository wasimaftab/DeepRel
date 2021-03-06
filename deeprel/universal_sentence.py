"""
Usage:
    universal_sentence [options] --output=<file> --input=<file>

Options:
    --verbose
    --output=<file>
    --input=<file>
    --skip
"""

import logging
from os import PathLike
from pathlib import Path
from typing import List

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from utils import parse_args, to_path
from deeprel import utils
from utils2 import pick_device

MODULE_URL = "https://tfhub.dev/google/universal-sentence-encoder-large/2"


def read_corpus(filename: Path) -> List[str]:
    messages = []
    for i, (obj, ex) in enumerate(utils.example_iterator2(filename)):
        words = []
        for tok in ex['toks']:
            if tok['type'] == 'O':
                words.append(tok['word'])
            else:
                words.append(tok['type'])
        messages.append(' '.join(words))
    return messages


def transform(src: Path, dst: PathLike):
    # Import the Universal Sentence Encoder's TF Hub module
    embed = hub.Module(MODULE_URL)
    tf.logging.set_verbosity(tf.logging.ERROR)
    logging.debug('Transforming')
    test_corpus = read_corpus(src)
    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        x = session.run(embed(test_corpus))
    logging.debug('Save to %s', dst)
    np.savez(dst, x=x)


def read_universal_sentence(filename):
    npzfile = np.load(filename)
    return npzfile['x']


if __name__ == '__main__':
    argv = parse_args(__doc__)

    # pick_device()

    output = to_path(argv['--output'])
    if not argv['--skip'] or not output.exists():
        transform(to_path(argv['--input']), output)
