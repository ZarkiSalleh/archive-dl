import json
import os
import DownloadItem
import config
import Archive 


item_metadata = Archive.get_metadata("COLLECTION_NAME")
file = item_metadata["files"][0]
url = f"https://archive.org/download/{item_metadata['metadata']['identifier']}/{file['name']}"
a = Archive.authenticate(config.U, config.P)
b = DownloadItem.DownloadItem(url, 10, 1048576, file['md5'], a)
print(b.resource_location_url)
b.download_resource()
b.rebuild_resource()
print(b.validate_resource_md5())