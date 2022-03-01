import time
from vncorenlp import VnCoreNLP
import pandas as pd

import threading
from multiprocessing import Pool

import string, re

class Clean_data:
  
  def __init__(self, data_raw):
    self.data = data_raw.copy()
  
  def f_base(self, s):
    """
    :param s: string to be processed
    :return: processed string: see comments in the source code for more info
    """

    s = s.replace("\n", " ")
    
    # normalization 1: xxxThis is a --> xxx. This is a (missing delimiter)
    #s = re.sub(r'([a-z])([A-Z])', r'\1\. \2', s)  # before lower case
    # normalization 2: lower case
    
    # s = s.lower()
    # normalization 3: "&gt", "&lt"
    s = re.sub(r'&gt|&lt', ' ', s)
    # normalization 4: letter repetition (if more than 2)
    s = re.sub(r'([a-z])\1{2,}', r'\1', s)
    # normalization 5: non-word repetition (if more than 1)
    s = re.sub(r'([\W+])\1{1,}', r'\1', s)
    # normalization 6: string * as delimiter
    s = re.sub(r'\*|\W\*|\*\W', '. ', s)
    # normalization 7: stuff in parenthesis, assumed to be less informal
    s = re.sub(r'\(.*?\)', '. ', s)
    # normalization 8: xxx[?!]. -- > xxx.
    s = re.sub(r'\W+?\.', '.', s)
    # normalization 9: [.?!] --> [.?!] xxx
    s = re.sub(r'(\.|\?|!)(\w)', r'\1 \2', s)
    # normalization 12: phrase repetition
    s = re.sub(r'(.{2,}?)\1{1,}', r'\1', s)

    return s.strip()

    
  def job(self, x):
    return self.f_base(x)

  def f_base_2(self, s=None):
    if s is None:
      s = self.data

    with Pool(4) as p:
      s['content'] = p.map(self.job, s['content'])
    
    # s['content'] = s['content'].map(lambda x: self.f_base(x))
    s['content_lower_case'] = s['content'].map(lambda x: x.lower())
    return s

  def preprocess_document(self, stopword_list=[]):
    self.f_base_2()
    return self.create_token_list(stopword_list=stopword_list)


  def create_token_list(self, s=None, stopword_list=[]):

    if s is None:
      s = self.data

    t1 = time.time()
    tmp_df = s['content']
    rdrsegmenter = VnCoreNLP("./src/VnCoreNLP/VnCoreNLP-1.1.1.jar", annotators="wseg,pos", max_heap_size='-Xmx2g')
    tmp_df = tmp_df.map(lambda x: rdrsegmenter.annotate(x)['sentences'])
    print("Done segmentation. Time: ", time.time() - t1)

    sentences = []
    for article in tmp_df:
      texts = []
      if article is None:
        continue
      for paragraph in article:
        texts.append(" ".join([x["form"] for x in paragraph]))
      sentences.append(" ".join(texts))

    tokens_list = []
    for article in tmp_df:
      tokens = []
      if article is None:
        continue
      for paragraph in article:
        for word in paragraph:
          if word['form'] not in stopword_list and word['posTag'] in ["N", "V", "A", "Np"]:
            tokens.append(word['form'])
      tokens_list.append(str(tokens))

    s["segmented"] = sentences
    s["tokens"] = tokens_list

    return s

if __name__ == "__main__":
    stopword_list = []

    with open('./data/vietnamese-stopwords-dash.txt', encoding="utf-8") as f:
      stopword_list = f.readlines()

    stopword_list = [word.replace("\n", '') for word in stopword_list]
    assert stopword_list
    
    print(stopword_list[:5])

    t1 = time.time()

    dataset = pd.read_csv('C:/Users/hahuy/OneDrive/Work/School/Thesis_TrendDetection/data/suc-khoe-articles.csv')
    dataset = dataset.dropna()[:300]
    print(dataset.tail())

    test = Clean_data(dataset)
    processed_data = test.preprocess_document(stopword_list=stopword_list)
    
    processed_data.drop(['author', 'excerpt', 'content', 'url', 'comments', 'tags', 'likes'], axis=1, inplace=True)
    
    processed_data.info()
    
    processed_data.to_csv("./data/t2_cleansed-tokenized-suc-khoe-articles.csv")

    print("Time taken:", time.time() - t1)

