import argparse
import csv
import cPickle as pickle
import collections
from HTMLParser import HTMLParser
import operator
import re
import json
import random
from SPARQLWrapper import SPARQLWrapper, JSON

import sklearn.preprocessing

# # Taken from
# # https://github.com/tensorflow/tensorflow/blob/16254e75e2fe4bb0f879b45fbad0c4b62c028011/tensorflow/models/rnn/translate/data_utils.py#L43
# _WORD_SPLIT = re.compile(b"([.,!?\"':;)(])")


# def basic_tokenizer(split_sentence):
#   """Very basic tokenizer: split the sentence into a list of tokens."""
#   words = []
#   for space_separated_fragment in split_sentence:
#     words.extend(re.split(_WORD_SPLIT, space_separated_fragment))
#   return [w for w in words if w]


def read_msr_recipes(data_list, url_list):
  recipes_by_url = {}
  for each in zip(url_list, data_list):

    # replace channels and functions with there catagories 
    parent_chan = []
    parent_func = []
    for word in (each[1][5], each[1][8]):
      if word == '500px':
        word = 'px500px'
      word = word.replace(' ', '')
      query_str = """
        SELECT ?object
        WHERE {{<http://elite.polito.it/ontologies/eupont-ifttt.owl#{}> <http://elite.polito.it/ontologies/eupont.owl#hasCategory> ?object}}
	  """.format(''.join(filter(str.isalnum, word.lower())))
      query = SPARQLWrapper('http://202.120.40.28:4460/ifttt/query')
      query.setQuery(query_str)
      query.setReturnFormat(JSON)
      query_result = query.query().convert()
      try:
        parent_chan.append(query_result['results']['bindings'][0]['object']['value'].replace('http://elite.polito.it/ontologies/eupont-ifttt.owl#', ''))
      except Exception:
        parent_chan.append(word)

    query_str = """
      SELECT ?object
      WHERE {{<http://elite.polito.it/ontologies/eupont-ifttt.owl#trigger{}{}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?object}}
    """.format(''.join(filter(str.isalnum, each[1][5].lower())), ''.join(filter(str.isalnum, each[1][6].lower())))
    query = SPARQLWrapper('http://202.120.40.28:4460/ifttt/query')
    query.setQuery(query_str)
    query.setReturnFormat(JSON)
    query_result = query.query().convert()
    try:
      parent_func.append(query_result['results']['bindings'][1]['object']['value'].replace('http://elite.polito.it/ontologies/eupont.owl#', ''))
    except Exception:
      parent_func.append(each[1][6])

    query_str = """
      SELECT ?object
      WHERE {{<http://elite.polito.it/ontologies/eupont-ifttt.owl#action{}{}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?object}}
    """.format(''.join(filter(str.isalnum, each[1][8].lower())), ''.join(filter(str.isalnum, each[1][9].lower())))
    query = SPARQLWrapper('http://202.120.40.28:4460/ifttt/query')
    query.setQuery(query_str)
    query.setReturnFormat(JSON)
    query_result = query.query().convert()
    try:
      parent_func.append(query_result['results']['bindings'][1]['object']['value'].replace('http://elite.polito.it/ontologies/eupont.owl#', ''))
    except Exception:
      parent_func.append(each[1][9])

    recipe = {
      'url': each[0],
      'id': each[1][0],
      'recipe': each[1][1],
      'trigger_chan': parent_chan[0],
      'trigger_func': parent_chan[0] + '.' + parent_func[0],
      'trigger_func_pure': parent_func[0],
      'trigger_param': None,
      'action_chan': parent_chan[1],
      'action_func': parent_chan[1] + '.' + parent_func[1],
      'action_func_pure': parent_func[1],
      'action_param': None,
	  'user_answer': each[1][1]
    }
    recipes_by_url[each[0]] = recipe
  return recipes_by_url


def parse_msr(data_list, url_list, extra_train, train_urls, dev_urls, test_urls,
              test_turk):
  train_urls = [line.strip() for line in train_urls]
  dev_urls = [line.strip() for line in dev_urls]
  test_urls = [line.strip() for line in test_urls]

  recipes_by_url = read_msr_recipes(data_list, url_list)
  if extra_train:
    extra_train_recipes = None
  else:
    extra_train_recipes = None

  data = {}
  for section_name, section_urls in zip(
      ['train', 'dev', 'test'], [train_urls, dev_urls, test_urls]):
    data[section_name] = {}
    for m in ['trigger', 'action']:
      data[section_name][m] = []
      for url in section_urls:
        r = recipes_by_url.get(url, None)
        if r is None:
          continue
        data[section_name][m].append({'url': r['url'],
                                      'id': r['id'],
                                      'recipe': r['recipe'],
                                      'chan': r[m + '_chan'],
                                      'func': r[m + '_func'],
                                      'param': r[m + '_param']})
      if section_name == 'train' and extra_train_recipes:
        for r in extra_train_recipes.itervalues():
          data[section_name][m].append({'url': r['url'],
                                        'id': r['id'],
                                        'recipe': r['recipe'],
                                        'chan': r[m + '_chan'],
                                        'func': r[m + '_func'],
                                        'param': r[m + '_param']})

  if test_turk:
    reader = csv.DictReader(test_turk, delimiter='\t')
    data_by_url = collections.defaultdict(list)
    for row in reader:
      data_by_url[row['URL']].append(row)

    tagged_urls = collections.defaultdict(set)
    # omitting descriptions marked as non-English by a majority of the
    # crowdsourced workers
    english_urls = set()
    # omitting descriptions marked as either non-English or unintelligible by
    # the crowd
    intelligible_urls = set()
    # only recipes where at least three of five workers agreed with the gold
    # standard
    gold_urls = set()

    for url, rows in data_by_url.iteritems():
      non_english = 0
      unintelligible = 0
      gold = 0
      for row in rows:
        descs = (row['Trigger channel'], row['Trigger'], row['Action channel'],
                 row['Action'])

        if 'nonenglish' in descs:
          non_english += 1
          unintelligible += 1
          continue
        if 'unintelligible' in descs:
          unintelligible += 1
          continue

        descs = tuple(desc.replace(' ', '_') for desc in descs)

        gold_recipe = recipes_by_url.get(url, None)
        if gold_recipe is not None:
          if descs == (gold_recipe['trigger_chan'], gold_recipe['trigger_func_pure'],
                       gold_recipe['action_chan'], gold_recipe['action_func_pure']):
            gold += 1

      threshold = float(len(rows)) / 2
      if non_english < threshold:
        tagged_urls['english'].add(url)
      if unintelligible < threshold:
        tagged_urls['intelligible'].add(url)
      if gold > threshold:
        tagged_urls['gold'].add(url)
  else:
    tagged_urls = {}

  return data, tagged_urls


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--output', required=True)
  parser.add_argument('--log', help='Path to log from MSR crawler')
  parser.add_argument('--extra-train')
  parser.add_argument('--train-urls',
                          help='List of URLs to use for training.')
  parser.add_argument('--dev-urls',
                          help='List of URLs to use for development.')
  parser.add_argument('--test-urls',
                          help='List of URLs to use for testing.')
  parser.add_argument('--test-turk', help='MTurk results on test set.')
  parser.add_argument('--input-file', required=True)

  args = parser.parse_args()

  input_data_list = []
  url_list = []
  with open(args.input_file) as in_file:
    input_data_list = in_file.readlines()
    
    input_data_list = [each[:-1].split('\t') for each in input_data_list]
    # a list of [id,description,author,date,shares,triggerchannel,trigger,
    #            triggerdescription,actionchannel,action,actiondescription]
    url_list = ['https://ifttt.com/recipes/{}-{}'.format(each[0], '-'.join(each[1][:-1].split(' '))).lower() for each in input_data_list]
    # a list of 'https://ifttt.com/recipes/[id]-[title]', url of ifttt recipe.
    # same order as the data list
 
  dev_thres = 0.8
  test_thres = 0.9
  train_urls = []
  dev_urls = []
  test_urls = []
  for each in url_list:
    rd = random.random()
    if rd < dev_thres:
      train_urls.append(each)
    elif rd < test_thres:
      dev_urls.append(each)
    else:
      test_urls.append(each)
  # split dataset


  data, tagged_urls = parse_msr(input_data_list, url_list, None, train_urls, dev_urls, test_urls, None)
  # Assign IDs to each word and label in the training data
  vocab = collections.Counter()
  for item in data['train']['action']:
    for word in item['recipe'][:-1].split(' '):
      vocab[word] += 1
  words_dec_freq = sorted(vocab.iteritems(),
                          key=operator.itemgetter(1),
                          reverse=True)
  word_ids = {k: i for i, (k, count) in enumerate(words_dec_freq)}


  # Make {train,test}_{trigger,action}_{channels,functions}.
  all_labels = collections.defaultdict()
  labelers = {}
  for m in ['trigger', 'action']:
    for n in ['chans', 'funcs']:
      label_type = m + '_' + n
      labels = {}

      for section in ['train', 'test', 'dev']:
        if section not in data: continue
        labels[section] = map(operator.itemgetter(n[:-1]), data[section][m])

      labeler = sklearn.preprocessing.LabelEncoder()
      labeler.fit(labels['train'] + labels['dev'] + labels['test'])

      for section in ['train', 'test', 'dev']:
        if section not in data: continue
        labels[section] = labeler.transform(labels[section])

      all_labels[label_type] = labels
      labelers[label_type] = labeler

  label_types = ('trigger_chans', 'trigger_funcs', 'action_chans',
                 'action_funcs')

  train_params = {}
  for section in ['train', 'test', 'dev']:
    for m in ['trigger','action']:
      for item in data[section][m]:
        params = item['param']
        if not (m+'/'+item['func'] in train_params):
          train_params[m+'/'+item['func']] = {}

  for m in ['trigger','action']:
    for item in data['train'][m]:
        params = item['param']
        for param_name in train_params[m+'/'+item['func']]:
          param_value = '<NULL>'
          if param_value == '<NULL>':
            train_params[m+'/'+item['func']][param_name][param_value] += 1

  predicted_params = {}
  param_num = {}
  for func_name in train_params:
    if not (func_name in predicted_params):
      predicted_params[func_name] = {}
      param_num[func_name] = 0
    for param_name in train_params[func_name]: 
      param_values = train_params[func_name][param_name]
      predicted_value = sorted(param_values.iteritems(), key=operator.itemgetter(1), reverse=True)[:1]
      if predicted_value[0][0] != '' and (train_params[func_name][param_name]['<NULL>'] == train_params[func_name][param_name][predicted_value[0][0]] or train_params[func_name][param_name][predicted_value[0][0]] <= 1):
        predicted_params[func_name][param_name] = '<NULL>'
      else:
        predicted_params[func_name][param_name] = predicted_value[0][0]
      if predicted_params[func_name][param_name] != '<NULL>':
        param_num[func_name] += 1

  outputs = {}
  for section in ['train', 'test', 'dev']:
    if section not in data: continue
    output = []
    for i in xrange(len(data[section]['action'])):
      words = data[section]['action'][i]['recipe'].split(' ')
      item = {'ids': [word_ids.get(word, len(word_ids)) for word in words],
              'labels': [all_labels[t][section][i] for t in label_types],
              'label_names': [labelers[t].classes_[all_labels[t][section][i]]
                              for t in label_types],
              'words': words, 
              'params': [data[section][t][i]['param'] for t in ['trigger','action']]}
      correct_trigger_param = 0
      correct_action_param = 0
      semi_correct_trigger_param = 0
      semi_correct_action_param = 0
      for param_name in train_params['trigger'+'/'+item['label_names'][1]]:
        truth = '<NULL>'
        for param in data[section]['trigger'][i]['param']:
          if param[0] == param_name:
            truth = param[1]
            break 
        if predicted_params['trigger'+'/'+item['label_names'][1]][param_name] == truth and truth != '<NULL>':
          correct_trigger_param += 1
        else:
          if truth != '<NULL>' and predicted_params['trigger'+'/'+item['label_names'][1]][param_name] != '<NULL>':
            semi_correct_trigger_param += 1
      for param_name in train_params['action'+'/'+item['label_names'][3]]:
        truth = '<NULL>'
        for param in data[section]['action'][i]['param']:
          if param[0] == param_name:
            truth = param[1]
            break
        if predicted_params['action'+'/'+item['label_names'][3]][param_name] == truth  and truth != '<NULL>':
          correct_action_param += 1
        else:
          if truth != '<NULL>' and predicted_params['action'+'/'+item['label_names'][3]][param_name] != '<NULL>':
            semi_correct_action_param += 1 
      item['correct_trigger_param'] = correct_trigger_param
      item['correct_action_param'] = correct_action_param
      item['semi_correct_trigger_param'] = semi_correct_trigger_param
      item['semi_correct_action_param'] = semi_correct_action_param
      if 'url' in data[section]['action'][i]:
        item['url'] = data[section]['action'][i]['url']
        tags = []
        for tag_name, tag_set in tagged_urls.iteritems():
          if item['url'] in tag_set:
            tags.append(tag_name)
        if tags:
          item['tags'] = tags

      output.append(item)
    outputs[section] = output
  outputs['label_types'] = label_types
  outputs['labelers'] = labelers
  outputs['word_ids'] = word_ids
  outputs['num_labels'] = [len(labelers[t].classes_) for t in label_types]
  outputs['train_params'] = train_params
  outputs['predicted_params'] = predicted_params
  outputs['param_num'] = param_num

  pickle.dump(outputs, open(args.output, 'w'), pickle.HIGHEST_PROTOCOL)
