from search import indriDocFetch, indriHandler, queryBuilder
from clir import cloud_stats
import codecs,os
class question(object):
    def __init__(self, id,type, tr, eng, answer=None):
        self.id = id
        self.type = type
        self.tr = tr.strip('?').replace("/"," ")
        self.eng = eng.strip('?').replace("/"," ")
        self.answer = answer.lower()
        self.clouds = []
        self.has_answer = []

    def search(self,query_dir = queryBuilder.queryDir):
        param_filename =  os.path.join(query_dir, str(self.id))
        try:
            param_file = codecs.open(param_filename,"r","utf-8")
        except IOError:
            queryBuilder.buildIndriQuerySingleFromQuestion(self.id, self.eng)
            #param_file = open(param_filename,"r")
        doc_ids = indriHandler.singleIndriQuery(self.id)
        doc_dir = os.path.join(query_dir, "docs",  str(self.id))
        if not os.path.exists(doc_dir):
            os.makedirs(doc_dir)

        for ind,doc_id in enumerate(doc_ids):
            doc = indriDocFetch.getDoc(doc_id)
            doc_decoded = doc.decode('utf-8')
            with codecs.open(os.path.join(doc_dir, str(ind)),'w+', 'utf-8') as q_file:
                q_file.write(doc_decoded)

    def build_word_clouds(self, query_dir = queryBuilder.queryDir):
        doc_dir = os.path.join(query_dir, "docs",  str(self.id))
        for _, _, filenames in os.walk(doc_dir):
            # print path to all filenames.
            for filename in filenames:
                doc_filename = os.path.join(doc_dir, filename)
                text,_ = cloud_stats.parse_document(doc_filename,self.eng)
                w_c = cloud_stats.calculate_wordcloud(text)
                self.clouds.append(w_c)
                #show_wordcloud(w_c)
                exists = False
                for word in self.answer.split(' '):
                    if(word in text):
                        exists = True
                        break
                for word in self.answer.split(' '):
                    for ind,(terms, freq) in enumerate(w_c.words_):
                        if word == terms:
                            print(ind+1,word, freq)
                            break
                self.has_answer.append(exists)


    def have_answer_in_cloud(self):
        for cloud_ind in range(0,len(self.clouds)):
            for ind,(word, freq) in enumerate(self.clouds[cloud_ind].words_):
                if word == self.answer:
                    print(ind+1,word, freq)
                    continue
            print("no")
