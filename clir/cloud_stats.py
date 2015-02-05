#!/usr/bin/python
import nltk, re, pprint
from nltk import word_tokenize, sent_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import itertools
from wordcloud import WordCloud
from matplotlib import pyplot as plt
import sys
import codecs

# pip install git+git://github.com/amueller/word_cloud.git

def calculate_wordcloud(text,max_words=100):
    return WordCloud(background_color="white",max_words=max_words,margin=10).generate(text)

def show_wordcloud(wordcloud):
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()

#query = "Which continent has the highest population?"
def parse_document(filename,query):
    myfile = codecs.open(filename,"r","utf-8")
    raw = myfile.read()
    sentences = sent_tokenize(raw)
    tokenizer = RegexpTokenizer(r'\w+') #tokenizer.tokenize(sentences[0])
    stop = stopwords.words('english')

    sents = [[token.lower() for token in tokenizer.tokenize(sentence) if
               not(token in stop or token.isdigit())] for sentence in sentences]

    query_t = [token for token in tokenizer.tokenize(query) if not(token in stop or token.isdigit())]
    cloud = " ".join(list(itertools.chain(*sents)))
    return cloud,query_t

def main(filename,query):
    text,_ = parse_document(filename,query)
    w_c = calculate_wordcloud(text)
    show_wordcloud(w_c)

if __name__ == '__main__':
    print("Hello",sys.argv[1],sys.argv[2])
    if len(sys.argv) > 2:
        main(sys.argv[1],sys.argv[2])
