import sys

sys.path.append('../')
from Database import Database 

word_tablename = 'companies'

db = Database('../dbcfg.ini').connect()

def get_indices(text, word, splitter = ' '):
    indices = []
    for i, w in enumerate(text.split(splitter)):
        if word.lower() in w.lower():
            indices.append(i)
    return indices

def line(l):
    link = l[0]
    synonym = l[1]
    tag = l[2]
    text = l[3]

    sentences = [sen.strip() for sen in text.split('.')]


    for i in range(len(sentences)):
        sentence = sentences[i]

        if synonym.lower() in sentence.lower():
            db.execute('INSERT INTO ' + word_tablename + '_training_data (link, synonym, sentence, positions) VALUES (%s, %s, %s, %s)', (link, synonym, sentence, get_indices(sentence, synonym)))
    
    
    
    

db.execute_and_run('SELECT b.link, b.synonym, b.tag, a.content FROM ' + word_tablename + ' as b INNER JOIN articles a on b.link = a.link;', attributes=(), callback=line, progress_bar=True)
