from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import socket
import sys

import deepnovo_config
import deepnovo_model
import deepnovo_worker_db
import deepnovo_worker_denovo
import deepnovo_worker_io
import deepnovo_worker_test
import deepnovo_main_modules


def main(_):
  hostname = socket.gethostname()
  print('hostname:', hostname)

  print("main()")

  if deepnovo_config.FLAGS.knapsack_build:
    deepnovo_main_modules.knapsack_build()
  elif deepnovo_config.FLAGS.train:
    deepnovo_main_modules.train()
  elif deepnovo_config.FLAGS.test_true_feeding:
    deepnovo_main_modules.test_true_feeding()
  elif deepnovo_config.FLAGS.decode:
    deepnovo_main_modules.decode()
  elif deepnovo_config.FLAGS.multi_decode:
    deepnovo_main_modules.multi_decode()
  elif deepnovo_config.FLAGS.multi_train:
    if deepnovo_config.data_format == 'mgf':
      deepnovo_main_modules.multi_train()
    elif deepnovo_config.data_format == 'pickle':
      deepnovo_main_modules.multi_train_pickles()
  elif deepnovo_config.FLAGS.sigopt:
    deepnovo_main_modules.sigopt()
  elif deepnovo_config.FLAGS.search_denovo:
    model = deepnovo_model.ModelInference()
    model.build_model()
    worker_io = deepnovo_worker_io.WorkerIO(
        input_file=deepnovo_config.denovo_input_file,
        output_file=deepnovo_config.denovo_output_file)
    worker_denovo = deepnovo_worker_denovo.WorkerDenovo()
    worker_denovo.search_denovo(model, worker_io)
  elif deepnovo_config.FLAGS.search_db:
    model = deepnovo_model.ModelInference()
    model.build_model()
    worker_io = deepnovo_worker_io.WorkerIO(
        input_file=deepnovo_config.db_input_file,
        output_file=deepnovo_config.db_output_file)
    worker_db = deepnovo_worker_db.WorkerDB()
    worker_db.build_db()
    worker_db.search_db(model, worker_io)
  elif deepnovo_config.FLAGS.search_hybrid:
    model = deepnovo_model.ModelInference()
    model.build_model()
    # denovo search
    worker_io = deepnovo_worker_io.WorkerIO(
        input_file=deepnovo_config.hybrid_input_file,
        output_file=deepnovo_config.hybrid_denovo_file)
    worker_denovo = deepnovo_worker_denovo.WorkerDenovo()
    predicted_denovo_list = worker_denovo.search_denovo(model, worker_io)
    # db search with predicted_denovo_list
    worker_io = deepnovo_worker_io.WorkerIO(
        input_file=deepnovo_config.hybrid_input_file,
        output_file=deepnovo_config.hybrid_output_file)
    worker_db = deepnovo_worker_db.WorkerDB()
    worker_db.build_db()
    worker_db.search_db(model, worker_io, predicted_denovo_list)
  elif deepnovo_config.FLAGS.test:
    worker_test = deepnovo_worker_test.WorkerTest()
    worker_test.test_accuracy()
  else:
    print("ERROR: wrong option!")
    sys.exit()


if __name__ == "__main__":
  tf.app.run()
