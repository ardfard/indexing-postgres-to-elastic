# pytype: skip-file

import argparse
import logging

import apache_beam as beam
from apache_beam.transforms import window

TABLE_SCHEMA = (
    "word:STRING, count:INTEGER, " "window_start:TIMESTAMP, window_end:TIMESTAMP"
)


def find_words(element):
    import re

    return re.findall(r"[A-Za-z\']+", element)


class FormatDoFn(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        ts_format = "%Y-%m-%d %H:%M:%S.%f UTC"
        window_start = window.start.to_utc_datetime().strftime(ts_format)
        window_end = window.end.to_utc_datetime().strftime(ts_format)
        return [
            {
                "word": element[0],
                "count": element[1],
                "window_start": window_start,
                "window_end": window_end,
            }
        ]


def main(argv=None):
    """Build and run the pipeline."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_topic",
        required=True,
        help='Input PubSub topic of the form "/topics/<PROJECT>/<TOPIC>".',
    )
    parser.add_argument(
        "--output_table",
        required=True,
        help=(
            "Output BigQuery table for results specified as: "
            "PROJECT:DATASET.TABLE or DATASET.TABLE."
        ),
    )
    known_args, pipeline_args = parser.parse_known_args(argv)
