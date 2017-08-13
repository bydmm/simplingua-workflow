# coding=utf-8
from __future__ import unicode_literals
import sys
import re
import string
from workflow import Workflow3, web, ICON_WEB

def get_dictionaries():
    url = 'https://simplingua.github.io/static/dictionaries.json'
    r = web.get(url)
    r.raise_for_status()
    return r.json()['dictionaries']

def filter_with_pattern(pattern, part, dictionaries):
    return list(filter(lambda entry: entry[part] and re.search(pattern, entry[part]), dictionaries))

def head_match(dictionaries, query):
    pattern = "^{query}.*".format(query=query)
    return filter_with_pattern(pattern, 'simplingua', dictionaries)

def body_match(dictionaries, query):
    pattern = "^(?!{query}).?{query}.*".format(query=query)
    return filter_with_pattern(pattern, 'simplingua', dictionaries)

def translation_match(dictionaries, query):
    pattern = "{query}.*".format(query=query)
    return filter_with_pattern(pattern, 'explain', dictionaries)

def main(wf):
     # Get query from Alfred
    if len(wf.args):
        query = wf.args[0]
    else:
        query = None

    # Retrieve dictionaries from cache if available and no more than 600
    dictionaries = wf.cached_data('dictionaries', get_dictionaries, max_age=600)

    if query:
        query = re.sub('[%s]' % re.escape(string.punctuation), '', query)
        query = re.sub("[+——！，。？、~@#￥%……&*（）]+", "", query)
        query = query.lower()
        words = query.split(' ')
        if len(words) > 1:
            for entry in dictionaries:
                if entry['simplingua'] and (entry['simplingua'] in words):
                    wf.add_item(entry['simplingua'], entry['explain'])
        else:
            headMatch = head_match(dictionaries, query)
            bodyMatch = body_match(dictionaries, query)
            translationMatch = translation_match(dictionaries, query)
            allMatch = headMatch + bodyMatch + translationMatch
            for entry in allMatch:
                wf.add_item(title=entry['simplingua'],
                            subtitle=entry['explain'],
                            arg=entry['simplingua'],
                            valid=True)
        wf.send_feedback()

if __name__ == u"__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
