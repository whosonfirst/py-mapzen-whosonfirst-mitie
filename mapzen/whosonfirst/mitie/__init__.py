# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import sys
sys.path.append('/usr/local/mapzen/mitie/MITIE/mitielib')

import mapzen.whosonfirst.search
import mapzen.whosonfirst.placetypes

import mitie

import copy
import logging

class ner_phrase:

    """
    an array of arrays containing (token, xrange, tag)
    """

    def __init__(self, raw):

        parts = []

        for p in raw:

            if not isinstance(p, (tuple,)):
                p = (p,)

            parts.append(p)

        logging.info("adding %s as a ner phrase" % parts)
        self.parts = parts

    def __repr__(self):

        tokens = list(self.tokens())
        return " ".join(tokens)

    def tokens(self):

        for p in self.parts:
            yield p[0]

    def entities(self):
        
        for p in self.parts:
            
            if len(p) == 3:
                yield p[1:3]

class ner_trainer:

    def __init__(self, dat, **kwargs):

        self.trainer = mitie.ner_trainer(dat)

    def get_by_id(self, id):
        raise Exception, "you need to implement this, silly"

    def index_feature(self, feature):

        for phrase in self.generate_phrases(feature):
            self.add_phrase(phrase)

    def generate_phrases(self, feature):
        
        props = feature['properties']

        if props.get('wof:placetype', None) != 'venue':
            logging.warning("I don't know how to generate phrases for this placetype")
            return

        wofid = props['wof:id']
        name = props['wof:name']
        
        tags = props.get('wof:tags', props.get('sg:tags', []))

        # pull in place names for the hierarchy/ies
        # generate and yield a bunch of phrase objects (above)

        hiers = props.get('wof:hierarchy', [])

        for t in tags:

            parts = [
                "I", "am", "going", "to",
                (name, xrange(4, 5), "venue"),
                "which", "is", "a",
                (t, xrange(8, 9), "tag"),                
            ]

            yield ner_phrase(parts)

            for h in hiers:
            
                for pt, p_id in h.items():

                    if int(p_id) == int(wofid):
                        continue

                    pt = pt.replace("_id", "")
                    pl = self.get_by_id(p_id)
                    
                    if not pl:
                        continue

                    pl_props = pl['properties']
                    pl_name = pl_props['wof:name']

                    # UGH ENCODING...

                    l_parts = copy.deepcopy(parts)

                    l_parts.append("in")
                    l_parts.append("the")
                    l_parts.append((pt, xrange(11,12), "placetype"))
                    l_parts.append("of")
                    l_parts.append((pl_name, xrange(13,14), pt))

                    yield ner_phrase(l_parts)

    def add_phrase(self, phrase):

        logging.info("add phrase %s" % phrase)

        tokens = list(phrase.tokens())
        sample = mitie.ner_training_instance(tokens)

        for idx, tag in phrase.entities():

            logging.info("%s at position %s" % (tag, idx))
            sample.add_entity(idx, tag)

        self.trainer.add(sample)

    def compile(self, dat):

        ner = self.trainer.train()
        ner.save_to_disk(dat)

class ner_trainer_es(ner_trainer):

    def __init__(self, dat, **kwargs):
        ner_trainer.__init__(self, dat)

        es = mapzen.whosonfirst.search.query(**kwargs)
        self.es = es

    def index_venues(self, **kwargs):
        
        logging.info("index all the venues")
        return self.index_placetype('venue', **kwargs)

    def index_placetype(self, placetype, **kwargs):

        placetype = mapzen.whosonfirst.placetypes.placetype(placetype)
        placetype_id = placetype.id()

        query = {
            'term': {
                'wof:placetype_id': placetype_id
            }
        }

        body = {
            'query': query,
        }
        
        self.index_features(body, **kwargs)
        
    def index_features(self, body, **kwargs):

        def index_rows(rows):

            logging.info("index rows")

            for row in rows:
                self.index_feature(row)

        self.search(body, index_rows, **kwargs)

    def get_by_id(self, id):

        query = {
            'ids': {
                'values': [id]
            }
        }
        
        body = {
            'query': query
        }
        
        rsp = self.es.search(body)
        docs = rsp['rows']

        try:
            return docs[0]
        except Exception, e:
            logging.error("failed to retrieve %s" % id)
            return None

    def search(self, body, cb, **kwargs):

        logging.info("search for %s" % body)

        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 100)

        pages = None

        # add a max_pages trigger...

        while not pages or page <= pages:

            args = { 'page': page, 'per_page': per_page }
            rsp = self.es.search(body, **args)

            pagination = rsp.get('pagination')
            rows = rsp.get('rows')

            cb(rows)
            break

            if not pages:
                pages = pagination['pages']

            page += 1

if __name__ == '__main__':

    import sys
    import logging

    logging.basicConfig(level=logging.INFO)

    dat = "/usr/local/mapzen/mitie/MITIE/MITIE-models/english/total_word_feature_extractor.dat"

    tr = ner_trainer_es(dat)
    tr.index_venues(per_page=10)
    tr.compile("foo.dat")
