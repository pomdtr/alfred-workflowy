import argparse
import os
import re
from re import MULTILINE
from uuid import uuid4

import requests
from urlparse import urlparse
from workflowy_api.transport import Operation, Transport


def uri_validator(uri):
    try:
        result = urlparse(uri)
        return all([result.scheme, result.netloc, result.path])
    except Exception:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("parent")
    parser.add_argument("text")
    args = parser.parse_args()

    text = args.text
    if uri_validator(args.text):
        try:
            res = requests.get(args.text)
            res.raise_for_status()
            match = re.search(
                "<title>(?:\\W+)(\w.+\w)(?:\\W+)</title>",
                res.text,
                re.MULTILINE | re.IGNORECASE,
            ).group(1)
            text = '<a href="{}">{}</a>'.format(args.text, match)
        except Exception:
            pass

    node_id = str(uuid4())
    operations = [
        Operation.create(node_id, args.parent),
        Operation.edit_name(node_id, text),
    ]

    session_id = os.getenv("session_id")
    transaction_id = os.getenv("transaction_id")
    Transport.push_and_poll(operations, session_id, transaction_id)
    print("Child created successfully !")
