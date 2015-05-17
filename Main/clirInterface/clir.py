import urllib2,sys
from urllib import quote

### IR #####
sys.path.append('irInterface')
from indriHandler import singleIndriQuery
import queryBuilder
############

key = "AIzaSyCDWvrBXpTFAfbcJqkyaVZrL_AwL2EM2pc"

def translate(text,target="tr",source="en",domain="google"):
    escaped_source = quote(text, '')
    google_url = "https://www.googleapis.com/language/translate/v2"
    full_url = "%s?q=%s&target=%s&format=text&source=%s&key=%s" %(google_url,target,source,escaped_source,key)
    req = urllib2.Request(url=full_url)
    r = urllib2.urlopen(req)
    res = r.read().decode('utf-8')
    return res

def translate_en(text,domain="google"):
    return translate(text,target="en",source="tr")

def query(question_en):
    paramFile="singleFromWeb_en"
    queryBuilder.buildIndriQuerySingle_en(paramFile, question_en)
    docs = singleIndriQuery(paramFile, count=3)
    return docs

def main(question_tr):
    question_en = translate(question_tr)
    docs = query(question_en)
    #docs_tr = translate_en(docs)
    return docs

#https://developers.google.com/apis-explorer/?hl=en_US#p/translate/v2/language.translations.list?q=T%25C3%25BCrkiyenin+en+b%25C3%25BCy%25C3%25BCk+ovas%25C4%25B1+hangisidir%253F&target=en&format=text&source=tr&_h=3&

#https://www.googleapis.com/language/translate/v2?q=T%C3%BCrkiye'nin+en+b%C3%BCy%C3%BCk+ovas%C4%B1+hangisidir%3F&target=en&format=text&source=tr&key=