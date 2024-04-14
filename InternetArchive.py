import requests
import logging


class InternetArchive:
    def __init__(self, url=None, collection=None, email=None, password=None, s3_access_key=None, s3_secret_key=None):
        self.url = url
        self.collection = collection

        if email and password and not (s3_access_key and s3_secret_key):
            self.authenticate(email, password)
        else:
            self.s3_access_key = s3_access_key
            self.s3_secret_key = s3_secret_key
            self.logged_in_user = None
            self.logged_in_sig = None

    def authenticate(self, email, password):
        url = "https://archive.org/services/xauthn/"
        params = {
            "op": "login",
        }
        data = {
            "email": email,
            "password": password,
        }
        response = requests.post(url, params=params, data=data)
        response.raise_for_status()
        response_json = response.json()
        self.s3_access_key = response_json["values"]["s3"]["access"]
        self.s3_secret_key = response_json["values"]["s3"]["secret"]
        self.logged_in_user = response_json["values"]["cookies"]["logged-in-user"]
        self.logged_in_sig = response_json["values"]["cookies"]["logged-in-sig"]

    # collection?
    def fetch_item_metadata(self):
        url = f"https://archive.org/metadata/{self.collection}"
        response = requests.get(url)
        response.raise_for_status()
        self.metadata = response.json()

    # collections contain items
    def is_item_restricted(self):
        # https://archive.org/developers/metadata-schema/#access-restricted-item
        if "access-restricted-item" in self.metadata["metadata"].keys():
            if self.metadata["metadata"]["access-restricted-item"] == "true":
                return True
            else:
                return False
        else:
            return False

    # items contain files
    def is_file_private(self, file_metadata):
        if "private" in file_metadata.keys():
            if file_metadata["private"] == "true":
                return True
            else:
                return False
        else:
            return False

    # i think perhaps load balance between the workable servers
    def set_workable_servers(self):
        if "workable-servers" in self.metadata["metadata"].keys():
            self.workable_servers = self.metadata["metadata"]["workable-servers"]
        else:
            self.workable_servers = None
