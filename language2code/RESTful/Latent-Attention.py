import tensorflow as tf
import flask
import numpy as np
import tf_utils
import _jsonnet

input_str = argv[1]
graph = tf.get_default_graph()
with tf.Session(graph=graph) as sess:
	saver = tf.train.import_meta_graph('../baselines/Latent-Attention/model/model.ckpt-66319.meta')
	sess.run(tf.global_variables_initializer())
	saver.restore(sess, '../baselines/Latent-Attention/model/model.ckpt-66319')
    (preds, ) = sess.run([mtest.preds], tf_utils.filter_none_keys({
        mtest.ids: ids,
        mtest.ids_lengths: ids_lengths,
        mtest.labels: labels,
    }))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--config')
  parser.add_argument('--load-model')
  args = parser.parse_args()

  if args.config:
    pretty_config_str = _jsonnet.evaluate_file(args.config)
    print pretty_config_str
    config = json.loads(pretty_config_str)
    ifttt_train = IftttTrain(args, config)
    try:
      ifttt_train.run(ifttt_train.initializer, args.load_model)
    except KeyboardInterrupt:
      pass

    print 'Config:'
    print pretty_config_str
    print 'Label names:', ifttt_train.label_type_names
    print 'Best accuracies:', ifttt_train.best_accuracy
    print 'Best iters:', ifttt_train.best_iters
    print 'Logdir:', args.logdir

