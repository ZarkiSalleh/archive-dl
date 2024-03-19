import requests

class Archive:
    def __init__(self, url = None, collection = None, s3_secret_key = None, s3_access_key = None, email = None, password = None):
        self.url = url
        self.collection = collection
        self.s3_secret_key = s3_secret_key
        self.s3_access_key = s3_access_key
        self.email = email
        self.password = password

        if self.email and self.password and not self.s3_secret_key and not self.s3_access_key:
            self.authenticate()
        else:
            self.auth = False
   
    def __authenticate(self):
        url = "https://archive.org/services/xauthn/"
        params = {
            'op': 'login',
        }
        data = {
            'email': self.email,
            'password': self.password,
        }
        response = requests.post(url, params=params, data=data)
        response.raise_for_status()
        response_json = response.json()
        self.s3_secret_key = response_json['values']['s3']['secret']
        self.s3_access_key = response_json['values']['s3']['access']
        self.logged_in_user = response_json['values']['cookies']['logged-in-user']  # unused
        self.logged_in_sig = response_json['values']['cookies']['logged-in-sig']  # unused
        self.auth = True

    def get_collection_metadata(identifier):
        url = f"https://archive.org/metadata/{identifier}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    # collections contain items
    def is_item_restricted(metadata):
        # https://archive.org/developers/metadata-schema/#access-restricted-item
        if "access-restricted-item" in metadata['metadata'].keys():
            if metadata['metadata']['access-restricted-item'] == 'true':
                return True
            else:
                return False
        else:
            return False

    # items contain files
    def is_file_private(file_metadata):
        if "private" in file_metadata.keys():
            if file_metadata["private"] == "true":
                return True
            else:
                return False
        else:
            return False