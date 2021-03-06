# pytype: skip-file

import argparse
import logging
import json
from os import pipe

import apache_beam as beam
from apache_beam.io.textio import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions, StandardOptions
from apache_beam.transforms.core import Map, ParDo
from apache_beam.transforms.util import WithKeys
from apache_beam.transforms.window import FixedWindows, TimestampedValue
import random
from elasticsearchio.writer import WriteToElasticSearch


class AddTimestamp(beam.DoFn):
    def process(self, element):
        ts = element["source"]["ts_ms"]
        logging.info(f"add timestamp to item: {ts}")
        yield TimestampedValue(element, ts)


class WriteToGcs(beam.DoFn):
    def __init__(self, output):
        self.output = output

    def process(self, key_value, window=beam.DoFn.WindowParam):
        ts_format = "%H:%M"
        window_start = window.start.to_utc_datetime().strftime(ts_format)
        window_end = window.end.to_utc_datetime().strftime(ts_format)
        shard_id, batch = key_value
        filename = "-".join([self.output, window_start,
                            window_end, str(shard_id)])
        logging.info(f"processing {key_value}")

        with beam.io.gcsio.GcsIO().open(filename=filename, mode="w") as f:
            for message_body in batch:
                logging.info(f"writing {message_body}")
                f.write(f"{message_body}\n".encode("utf-8"))


class ProcessPubsub(beam.PTransform):
    def __init__(self, topic):
        self.topic = topic

    def expand(self, pcoll):
        logging.info(f"Process {self.topic}")
        return (pcoll
                | "Read PubSub" >> beam.io.ReadFromPubSub(topic=self.topic)
                | "Parse JSON" >> beam.Map(json.loads)
                | "Windows into" >> beam.WindowInto(FixedWindows(15, 0))
                | "Add keys" >> WithKeys(lambda e: e['after']['item_id'])
                | "Get latest" >> beam.combiners.Latest.PerKey()
                )


def main(argv=None):
    """Build and run the pipeline."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topic_project_id",
        required=True,
        help=(
            "Project id for prefix"
        ),
    )
    parser.add_argument(
        "--elasticsearch_url",
        required=True,
        help=(
            "Elasticsearch url"
        ),
    )

    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    pipeline_options.view_as(StandardOptions).streaming = True
    topic_prefix = f"projects/{known_args.topic_project_id}/topics"

    logging.info(f"topic prefix: {topic_prefix}")

    with beam.Pipeline(options=pipeline_options) as p:
        (p
         | "Procces items" >> ProcessPubsub(f"{topic_prefix}/datastaging_test_debezium.public.items")
         | "Write items" >> WriteToElasticSearch(
             es_url=known_args.elasticsearch_url,
             index_name="tests",
             batch_size=20))

        (p
         | "Process items price" >> ProcessPubsub(f"{topic_prefix}/datastaging_test_debezium.public.item_prices")
         | "Write price" >> WriteToElasticSearch(
             es_url=known_args.elasticsearch_url,
             index_name="tests",
             batch_size=20))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main()
