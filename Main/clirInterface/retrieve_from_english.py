import urllib2,sys,json,os,io
from urllib import quote

### IR #####
sys.path.append('irInterface')
from indriHandler import singleIndriQuery
import queryBuilder,indriDocFetch
indriDocFetch.indexDir = queryBuilder.index_dir_tr
############

key = "AIzaSyCDWvrBXpTFAfbcJqkyaVZrL_AwL2EM2pc"
translation_dir = "../Data/wikipedia_translations"

def translate(text,source="tr",target="en",domain="google"):
    escaped_source = quote(text.encode('utf8'), '')
    google_url = "https://www.googleapis.com/language/translate/v2"
    full_url = "%s?q=%s&target=%s&format=text&source=%s&key=%s" %(google_url,escaped_source,target,source,key)
    req = urllib2.Request(url=full_url)
    try:
        r = urllib2.urlopen(req)
    except:
        sys.stderr.write("Something happened [%s...] couldn't translated\nUrl : %s\n" % (text[0:20],full_url))
        return None
    res = json.loads(r.read().decode('utf-8'))
    translations = res['data']['translations']
    if translations:
        return translations[0]['translatedText']
    return None

def translate_en(text,domain="google"):
    return translate(text,source="en",target="tr")

def fetch_and_translate(doc_id,doc_filename):
    doc_tuple = indriDocFetch.getDoc(doc_id)
    try:
        doc = "\n".join(doc_tuple)
    except TypeError:
        print("[Error ]Doc id: %s" %doc_id)
        return
    translated_doc = []
    for part in doc.split("\n"):
        if len(part) < 5000:
            part_translated = translate_en(part)
            translated_doc.append(part_translated)
        else:
            sys.stderr.write("Doc id %s [HTTP Error 413: Request Entity Too Large]" %doc_id)
    translated_doc_str = "\n".join(translated_doc)
    with io.open(doc_filename,"w") as doc_file:
        doc_file.write(translated_doc_str)
    return translated_doc_str

def query(question_en):
    paramFile="singleFromWeb_en"
    queryBuilder.buildIndriQuerySingle_en(paramFile, question_en.replace("'",""))
    doc_ids = singleIndriQuery(paramFile, count=3)
    translated_docs = []
    for doc_id in doc_ids:
        doc_filename = os.path.join(translation_dir, doc_id)
        if os.path.exists(doc_filename):
            with open(doc_filename) as doc_file:
                translated_docs.append("".join(doc_file.readlines()))
        else:
            translated_docs.append(fetch_and_translate(doc_id,doc_filename))
    return translated_docs

def main(question_tr):
    question_en = translate(question_tr)
    docs = query(question_en)
    #docs_tr = translate_en(docs)
    return docs

#https://developers.google.com/apis-explorer/?hl=en_US#p/translate/v2/language.translations.list?q=T%25C3%25BCrkiyenin+en+b%25C3%25BCy%25C3%25BCk+ovas%25C4%25B1+hangisidir%253F&target=en&format=text&source=tr&_h=3&

#https://www.googleapis.com/language/translate/v2?q=T%C3%BCrkiye'nin+en+b%C3%BCy%C3%BCk+ovas%C4%B1+hangisidir%3F&target=en&format=text&source=tr&key=
