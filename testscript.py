import HttpDownload

import HttpDownload

url = ""
threads = 10
chunk_size = 1048576
md5 = ""
dli = HttpDownload.HttpDownload(url, threads, chunk_size, md5)

# import json
# import os
# import DownloadItem
# import config
# import InternetArchive


# ia = InternetArchive.InternetArchive(collection="redump_pc_N")
# ia.fetch_item_metadata()
# file = ia.metadata["files"][0]
# print(json.dumps(file, indent=2))
# if ia.is_file_private(file):
#     print("File is private, authentication required")
#     ia.authenticate(config.U, config.P)
#     file_url = f"https://archive.org/download/{ia.metadata['metadata']['identifier']}/{file['name']}"
#     dli = DownloadItem.DownloadItem(file_url, 10, 1048576, file["md5"], ia.s3_access_key, ia.s3_secret_key)
#     print(dli.resource_location_url)
#     dli.download_resource()
#     dli.rebuild_resource()
#     if dli.validate_resource_md5():
#         print("Resource validated")
#     else:
#         print("Resource validation failed, md5 mismatch")

# item_metadata = Archive.get_metadata("COLLECTION_NAME")
# file = item_metadata["files"][0]
# url = f"https://archive.org/download/{item_metadata['metadata']['identifier']}/{file['name']}"
# a = Archive.authenticate(config.U, config.P)
# b = DownloadItem.DownloadItem(url, 10, 1048576, file["md5"], a)
# print(b.resource_location_url)
# b.download_resource()
# b.rebuild_resource()
# print(b.validate_resource_md5())
