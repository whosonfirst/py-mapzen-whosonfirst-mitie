# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import mapzen.whosonfirst.search
import mapzen.whosonfirst.placetypes

import mitie

class phrase:

    def __init__(self):
        pass

    def tokens(self):
        return []

    def entities(self):
        pass

class ner_trainer:

    def __init__(self, **kwargs):

        self.trainer = mitie.ner_trainer()

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

        name = props['wof:name']
        tags = props.get('wof:tags', props.get('sg:tags', []))

        # pull in place names for the hierarchy/ies
        # generate and yield a bunch of phrase objects (above)

    def add_phrase(self, phrase):

        sample = mitie.ner_training_instance(phrase.tokens())

        for idx, tag in phrase.entities():
            sample.add_entity(idx, tag)

        self.trainer.add(sample)

    def compile(self, dat):

        ner = self.trainer.train()
        ner.save_to_disk(dat)

class ner_trainer_es(ner_trainer):

    def __init__(self, **kwargs):
        trainer.__init__(self, **kwargs)

        es = mapzen.whosonfirst.search.query(**kwargs)
        self.es = es

    def index_venues(self, **kwargs):

        return self.index_placetype('venue', *kwargs)

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
        
        return self.index_features(self, body, **kwargs)
        
    def index_features(self, body, **kwargs):

        def index_rows(rows):

            for row in rows:
                self.index_feature(row)

        self.search(body, index_rows)

    def search(self, body, cb, **kwargs):
        
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 100)

        pages = None

        # add a max_pages trigger...

        while not pages or page <= pages:

            args = { 'page': page, 'per_page': per_page }
            rsp = self.es.search(body, args)

            pagination = rsp.get('pagination')
            rows = rsp.get('rows')

            cb(rows)

            if not pages:
                pages = pagination['pages']

            page += 1
