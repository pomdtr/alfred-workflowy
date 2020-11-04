import argparse
import os
from uuid import uuid4

from workflowy_api.transport import Operation, Transport


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("parent")
    parser.add_argument("text")
    args = parser.parse_args()

    node_id = str(uuid4())
    operations = [
        Operation.create(node_id, args.parent),
        Operation.edit_name(node_id, args.text),
    ]

    session_id = os.getenv("session_id")
    transaction_id = os.getenv("transaction_id")
    Transport.push_and_poll(operations, session_id, transaction_id)
    print("Child created successfully !")
