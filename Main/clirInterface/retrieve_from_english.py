# -*- coding: utf-8 -*-
import urllib2,sys,json,os,io
from urllib import quote

### IR #####
sys.path.append('irInterface')
from indriHandler import singleIndriQuery
import querybuilder,indridocfetch
indridocfetch.indexdir = querybuilder.index_dir_tr
############
DEBUG = False
api_key = "AIzaSyCDWvrBXpTFAfbcJqkyaVZrL_AwL2EM2pc"
translation_dir = "../Data/wikipedia_translations"
DOCS = {}
def translate(text,source="tr",target="en",domain="google"):
    escaped_text = quote(text.encode('utf8'), '')
    google_url = "https://www.googleapis.com/language/translate/v2"
    full_url="%s?q=%s&target=%s&format=text&source=%s&key=%s" %(google_url,escaped_text,target,source,api_key)
    req = urllib2.Request(url=full_url)
    try:
        response = urllib2.urlopen(req)
    except:
        ex = sys.exc_info()[0]
        sys.stderr.write("Something happened: %s\n[%s...] couldn't translated\nUrl : %s\n" % (ex,text[0:20],full_url))
        return text
    res = json.loads(response.read().decode('utf-8'))
    translations = res['data']['translations']
    if translations:
        return translations[0]['translatedText']
    else:
        sys.stderr.write("No translation received for [%s...]\n" % text[0:20])
        return text

def translate_en(text,domain="google"):
    return translate(text,source="en",target="tr")

def fetch_and_translate(doc_id,doc_filename):
    doc_title,doc = indriDocFetch.getDoc(doc_id)
    doc_title_translated = translate_en(doc_title)
    translated_doc = [doc_title_translated,]
    DOCS[doc_id] =  "%s (%s)" % (doc_title,doc_title_translated)
    for part in doc.split("\n"):
        if len(part) < 5000:
            part_translated = translate_en(part)
            translated_doc.append(part_translated)
        else:
            sys.stderr.write("Doc id %s [HTTP Error 413: Request Entity Too Large]\n" %doc_id)
    translated_doc_str = "\n".join(translated_doc)
    with io.open(doc_filename,"w") as doc_file:
        doc_file.write(translated_doc_str)
    return translated_doc_str

def query(question_en):
    param_file = "singleFromWeb_en"
    queryBuilder.buildIndriQuerySingle_en(param_file, question_en.replace("'",""))
    doc_ids = singleIndriQuery(param_file, count=3)
    translated_docs = []
    for doc_id in doc_ids:
        doc_filename = os.path.join(translation_dir, doc_id)
        if os.path.exists(doc_filename):
            with open(doc_filename) as doc_file:
                translated_docs.append("".join(doc_file.readlines()))
        else:
            translated_docs.append(fetch_and_translate(doc_id,doc_filename))
        if DEBUG:
            sys.stdout.write("[%s] %s\n" %(doc_id,DOCS.get(doc_id) or ""))
    return translated_docs

def main(question_tr):
    question_en = translate(question_tr)
    if DEBUG:
        sys.stdout.write("%s\n" % question_en)
    docs_list = query(question_en)
    #docs_tr = translate_en(docs)
    return docs_list

#https://developers.google.com/apis-explorer/?hl=en_US#p/translate/v2/language.translations.list?q=T%25C3%25BCrkiyenin+en+b%25C3%25BCy%25C3%25BCk+ovas%25C4%25B1+hangisidir%253F&target=en&format=text&source=tr&_h=3&

#https://www.googleapis.com/language/translate/v2?q=T%C3%BCrkiye'nin+en+b%C3%BCy%C3%BCk+ovas%C4%B1+hangisidir%3F&target=en&format=text&source=tr&key=

if __name__ == "__main__":
    print sys.argv
    with open("/home/hazircevap/hazircevap/Data/q.q") as q_q:
        lines = q_q.readlines()

    all_questions = []

    for line in lines:
        all_questions.append(line.split("|")[0])

    docs_dict = {}
    path = "../Data/wikipedia_translations/"
    for filename in next(os.walk(path))[2]:
        with open(os.path.join(path,filename)) as w_file:
            docs_dict[filename] = w_file.readline().strip()

    docs_dict['1217700'] = "İrlanda Cumhuriyeti"
    docs_dict['44265'] = "Waterford Waterford"
    docs_dict['29151'] = "Brno"
    docs_dict['960585'] = "Çukurova"
    docs_dict['1379071'] = "Doğu Anadolu Bölgesi"

    DOCS = docs_dict
    DEBUG = True
    i = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for ind,qu in enumerate(all_questions[i:]):
        sys.stdout.write("[%d] %s\n" %(ind+i,qu))
        docs_l = main(qu)
        sys.stdout.write("---------\n")
