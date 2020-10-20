import requests
import json
import sys
import string
import random

if sys.version_info.major == 3:
    from urllib.parse import quote
else:
    from urllib import quote


class WorkflowyException(Exception):
    pass


class Transport:
    LOGIN_URL = "https://workflowy.com/api/auth"
    INIT_URL = "https://workflowy.com/get_initialization_data"
    API_URL = "https://workflowy.com/push_and_poll"
    CLIENT_VERSION = 21
    mr_transaction_id = None

    @classmethod
    def send_code(cls, email):
        response = requests.post(
            cls.LOGIN_URL, data={"email": email, "allowSignup": False}
        )
        response.raise_for_status()

    @classmethod
    def login(cls, username, password="", code=""):
        response = requests.post(
            cls.LOGIN_URL, data={"email": username, "password": password, "code": code}
        )
        response.raise_for_status()

        session_id = response.cookies.get("sessionid")

        return session_id

    @classmethod
    def get_initialization_data(cls, session_id):
        response = requests.get(
            cls.INIT_URL,
            params={"client_version": cls.CLIENT_VERSION},
            cookies={"sessionid": session_id},
        )
        response.raise_for_status()
        response_body = response.json()
        transaction_id = response_body["projectTreeData"]["mainProjectTreeInfo"][
            "initialMostRecentOperationTransactionId"
        ]
        cls.mr_transaction_id = transaction_id

        return (
            response_body["projectTreeData"]["mainProjectTreeInfo"][
                "rootProjectChildren"
            ],
            json.loads(response_body["settings"]["saved_views_json"]),
            transaction_id,
        )

    @classmethod
    def push_and_poll(cls, operations, session_id, transaction_id=None):
        if transaction_id is None:
            transaction_id = cls.mr_transaction_id
        push_poll_data = [
            {
                "most_recent_operation_transaction_id": transaction_id,
                "operations": operations,
            }
        ]
        push_poll_data = quote(json.dumps(push_poll_data))
        try:
            response = requests.post(
                cls.API_URL,
                data="client_version={}&push_poll_data={}".format(
                    cls.CLIENT_VERSION, push_poll_data
                ),
                headers={
                    "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
                cookies={"sessionid": session_id},
            )

            response.raise_for_status()
        except Exception:
            raise WorkflowyException(
                "A problem occured. Is workflowy.com accessible from your network"
            )

        if not "results" in response.json() or "error" in response.json()["results"][0]:
            raise WorkflowyException(
                "Error: {} for operation {}".format(response.json(), push_poll_data)
            )
        
        cls.mr_transaction_id = response.json()["results"][0][
            "new_most_recent_operation_transaction_id"
        ]

        return response


class Operation:
    @staticmethod
    def edit_name(id, new_name):
        return {"type": "edit", "data": {"projectid": id, "name": new_name}}

    @staticmethod
    def edit_note(id, new_note):
        return {"type": "edit", "data": {"projectid": id, "description": new_note}}

    @staticmethod
    def create(id, parent_id):
        return {
            "type": "create",
            "data": {
                "projectid": id,
                "parentid": parent_id,
                "priority": 0,
            },
        }

    @staticmethod
    def complete(id):
        return {
            "type": "complete",
            "data": {
                "projectid": id,
            },
        }

    @staticmethod
    def uncomplete(id):
        return {
            "type": "uncomplete",
            "data": {
                "projectid": id,
            },
        }

    @staticmethod
    def delete(id):
        return {
            "type": "uncomplete",
            "data": {
                "projectid": id,
            },
        }

    @staticmethod
    def share(id):
        return {"type": "share", "data": {"project_id": id}}

    @staticmethod
    def add_shared_url(id, permission_level):
        return {
            "type": "add_shared_url",
            "data": {
                "projectid": id,
                "permission_level": permission_level,
                "access_token": "".join(
                    [
                        random.choice(string.ascii_letters + string.digits)
                        for _ in range(16)
                    ]
                ),
            },
        }
