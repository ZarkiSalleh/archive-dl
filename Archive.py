import requests


def authenticate(email, password):
    url = "https://archive.org/services/xauthn/"
    params = {
        'op': 'login',
    }
    data = {
        'email': email,
        'password': password,
    }
    response = requests.post(url, params=params, data=data)
    response.raise_for_status()
    response_json = response.json()
    return {
        's3': {
            'access': response_json['values']['s3']['access'],
            'secret': response_json['values']['s3']['secret'],
        },
        'cookies': {
            'logged-in-user': response_json['values']['cookies']['logged-in-user'],
            'logged-in-sig': response_json['values']['cookies']['logged-in-sig'],
        },
    }


def get_metadata(identifier):
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
