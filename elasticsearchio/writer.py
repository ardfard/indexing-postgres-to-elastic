from apache_beam.portability.api.beam_runner_api_pb2 import TimeDomain
from apache_beam.transforms import DoFn
from apache_beam.transforms import ParDo
from apache_beam.transforms import PTransform
from elasticsearch.helpers import bulk
import elasticsearch
import logging

# Code taken from https://github.com/rrmerugu/apache-beam-io-extras/blob/master/beam_io_extras/elasticsearch.py


class ElasticSearchWriteFn(DoFn):
    """
    ## Needed :
    pip install elasticsearch
    ## Usage:
    from elasticsearch import Elasticsearch
    es_client = Elasticsearch(hosts=["127.0.0.1:9200"], timeout=5000)
    """

    def __init__(self,
                 es_url=None,
                 index_name=None,
                 doc_type=None,
                 batch_size=None,
                 mapping=None):
        self.es_url = es_url
        self.index_name = index_name
        self.doc_type = doc_type
        self.mapping = mapping

        self.batch_size = batch_size
        self._max_batch_size = batch_size or 500

    def _pre_process_element(self, element):
        """
        Over ride this to extend
        :param element:
        :return:
        """
        return element

    def start_bundle(self):
        self._rows_buffer = []

    def process(self, element, unused_create_fn_output=None):
        self._rows_buffer.append(self._pre_process_element(element))
        logging.info(f"writing row: {element}")
        # TODO: also use timeout to flush buffer
        if len(self._rows_buffer) >= self._max_batch_size:
            self._flush_batch()

    def finish_bundle(self):
        if self._rows_buffer:
            self._flush_batch()
        self._rows_buffer = []

    def gen_index_action(self):
        for _, row in self._rows_buffer:
            doc = row['after']
            doc['_id'] = doc['item_id']
            yield doc

    def _flush_batch(self):
        logging.info("flushing buffer")
        success, _ = bulk(
            client=elasticsearch.Elasticsearch(hosts=[self.es_url]),
            actions=self.gen_index_action(),
            index=self.index_name,
            stats_only=True,
            raise_on_error=False)
        if success:
            logging.info("inserted {} docs into {}/{} ".format(len(self._rows_buffer),
                                                               self.index_name, self.doc_type))
        self._rows_buffer = []


class WriteToElasticSearch(PTransform):

    def __init__(self,
                 es_url=None,
                 index_name=None,
                 doc_type=None,
                 batch_size=None,
                 mapping=None):
        """
        Initialize a WriteToElasticSearch transform.
        """
        self.es_url = es_url
        self.index_name = index_name
        self.doc_type = doc_type
        self.mapping = mapping

        self.batch_size = batch_size

    def expand(self, pcoll):
        elasticsearch_write_fn = ElasticSearchWriteFn(
            es_url=self.es_url,
            index_name=self.index_name,
            doc_type=self.doc_type,
            mapping=self.mapping
        )
        return pcoll | 'WriteToElasticSearch' >> ParDo(elasticsearch_write_fn)
