import requests
from concurrent.futures import ThreadPoolExecutor
import os
import urllib.parse
import hashlib


class DownloadItem:
    def __init__(self, target_url, number_of_threads, chunk_size, md5_hash=None, auth=None):
        self.part_byte_ranges = []
        self.target_url = target_url
        self.number_of_threads = number_of_threads
        self.chunk_size = chunk_size
        self.resource_md5 = md5_hash
        self.auth = auth
        self.__fetch_resource_location_url()
        self.__fetch_resource_size()
        self.__calc_part_size()
        self.__calc_parts()
        self.__calc_resource_file_name()

    def __str__(self):
        return f"""resource: {self.resource_location_url}
size: {self.resource_size} bytes
part size: {self.part_size} bytes
part byte ranges: {self.part_byte_ranges}
"""

    def __fetch_resource_location_url(self):
        # will 302 to the actual resource
        response = requests.head(
            self.target_url
        )
        if 'Location' not in response.headers.keys():
            raise ValueError("Archive 'Location' header not found, cannot download")
        else:
            self.resource_location_url = response.headers['Location']

    def __calc_resource_file_name(self):
        encoded_file_name = self.resource_location_url.split("/")[-1]
        decoded_file_name = urllib.parse.unquote(encoded_file_name)
        self.resource_file_name = decoded_file_name

    def __fetch_resource_size(self):
        if self.auth:
            headers = {'Authorization': f'LOW {self.auth["s3"]["access"]}:{self.auth["s3"]["secret"]}'}
            response = requests.head(
                self.resource_location_url,
                headers=headers
            )
        else:
            response = requests.head(
                self.resource_location_url
            )
        if 'Content-Length' not in response.headers.keys():
            raise ValueError("Response doesn't contain 'Content-Length' header, cannot download")
        else:
            self.resource_size = int(response.headers['Content-Length'])

    def __calc_part_size(self):
        self.part_size = int(self.resource_size / self.number_of_threads)

    def __calc_parts(self):
        part_range_list = list(range(0, self.resource_size, self.part_size))
        if part_range_list[-1] < self.resource_size:  # normally doesn't divide evenly, so add the end
            part_range_list.append(self.resource_size)
        list_size = len(part_range_list)
        for i in range(list_size - 1):
            if i != list_size - 2:
                self.part_byte_ranges.append((part_range_list[i], part_range_list[i + 1] - 1))  # one byte before next
            else:
                self.part_byte_ranges.append((part_range_list[i], part_range_list[i + 1]))  # up to the end byte

    def __download_part(self, start_byte, end_byte):
        print(f"downloading part from byte {start_byte} - byte {end_byte}")
        headers={
            'Range': f"bytes={start_byte}-{end_byte}"
        }
        if self.auth:
            headers['Authorization'] = f"LOW {self.auth['s3']['access']}:{self.auth['s3']['secret']}"
        response = requests.get(
            url=self.resource_location_url,
            headers=headers,
            stream=True,
        )
        with open(f"dl-{start_byte}-{end_byte}.part", "wb") as out_file:
            for chunk in response.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    out_file.write(chunk)
        return response.status_code

    def download_resource(self):
        with ThreadPoolExecutor(max_workers=self.number_of_threads) as executor:
            futures = executor.map(self.__download_part, *zip(*self.part_byte_ranges))
            # TODO error handling for the threads e.g re-download failed parts

    def rebuild_resource(self):
        with open(self.resource_file_name, 'wb') as f:
            for start_byte, end_byte in sorted(self.part_byte_ranges):
                part_file_path = f"dl-{start_byte}-{end_byte}.part"
                with open(part_file_path, 'rb') as rf:
                    f.write(rf.read())
                os.remove(part_file_path)

    def validate_resource_md5(self):
        if self.resource_md5:
            with open(self.resource_file_name, 'rb') as f:
                md5_hash = hashlib.md5(f.read()).hexdigest()
                if md5_hash == self.resource_md5:
                    return True
                else:
                    return False
        else:
            raise ValueError("No initial MD5 Hash provided.")
