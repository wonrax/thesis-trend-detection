import time
import re, string
from vncorenlp import VnCoreNLP
import pandas as pd

class Clean_data:
  
  def __init__(self, data_raw):
    self.data_raw = data_raw
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

  def f_base_2(self, s):
    remove_digits = str.maketrans('', '' , string.digits)
    s['content'] = s['content'].map(lambda x: self.f_base(x))
    s['content_lower_case'] = s['content'].map(lambda x: x.lower())
    return s

  def preprocess_document(self):
   return self.f_base_2(self.data_raw)


  def create_token_list(self, s):

    rdrsegmenter = VnCoreNLP("VnCoreNLP/VnCoreNLP-1.1.1.jar", annotators="wseg,pos", max_heap_size='-Xmx2g') 

    tmp_df = s['content'].copy()
    tmp_df = tmp_df.map(lambda x: rdrsegmenter.annotate(x)['sentences'])
    s["sentences"] = tmp_df.map(lambda x: " ".join([" ".join([w['form'] for w in y]) for y in x]))
    s["token_lists"] = tmp_df.map(lambda x:sum( [[ y['form'].lower() for y in w if (y['posTag'] in ["N", "V", "A", "Np"] and y['form'] not in stopword_list) ] for w in x] , []))
    return s


  def create_store_file(self, name="demo"):
    D = self.preprocess_document()
    D = self.create_token_list(D)
    D.to_csv("cleanData" + str(name) +".csv")
    print("Success create " + name + ".csv" + "Ver 02")

if __name__ == "__main__":
    stopword_list = []

    with open('data/vietnamese-stopwords-dash.txt', encoding="utf-8") as f:
      stopword_list = f.readlines()

    stopword_list = [word.replace("\n", '') for word in stopword_list]
    assert stopword_list

    t1 = time.time()

    dataset = pd.read_csv('C:/Users/hahuy/OneDrive/Work/School/Thesis_TrendDetection/data/suc-khoe-articles.csv.backup5')
    dataset = dataset.dropna()
    print(dataset.head())

    Test = Clean_data(dataset[:50])
    processed_data = Test.preprocess_document()
    processed_data = Test.create_token_list(processed_data)
    
    processed_data.drop(['author', 'excerpt', 'content', 'url', 'comments', 'tags', 'likes'], axis=1, inplace=True)
    
    print(processed_data.head)
    
    processed_data.to_csv("cleansed-tokenized-suc-khoe-articles.csv")
    

    print("Time taken:", time.time() - t1)

