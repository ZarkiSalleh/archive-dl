import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import urllib.parse
import hashlib
import os


class HttpDownload:
    def __init__(
        self,
        target_url,
        number_of_threads,
        chunk_size,
        download_path=None,
        md5_hash=None,
        extra_headers=None,
    ):
        self.part_byte_ranges = []
        self.target_url = target_url
        self.number_of_threads = number_of_threads
        self.chunk_size = chunk_size
        self.resource_md5 = md5_hash
        self.__fetch_resource_location_url()
        self.__fetch_resource_size()
        self.__calc_part_size()
        self.__calc_parts()
        self.__calc_resource_file_name()
        self.__pre_allocate_space()
        self.download_resource()
        self.validate_resource_md5()

    def __fetch_resource_location_url(self):
        # will 302 to the actual resource
        response = requests.head(self.target_url)
        try:
            response.raise_for_status()
            if "Location" not in response.headers.keys():
                # raise ValueError("Archive 'Location' header not found, cannot download")
                print("resource is redirecting, using redirect url for resource")
                self.resource_location_url = self.target_url
            else:
                self.resource_location_url = response.headers["Location"]
        except Exception as e:
            print(e)

    def __calc_resource_file_name(self):
        encoded_file_name = self.resource_location_url.split("/")[-1]
        decoded_file_name = urllib.parse.unquote(encoded_file_name)
        self.resource_file_name = decoded_file_name

    def __fetch_resource_size(self):
        response = requests.head(self.resource_location_url)
        try:
            response.raise_for_status()
            if "Content-Length" not in response.headers.keys():
                raise ValueError("Response doesn't contain 'Content-Length' header, cannot download")
                # TODO - run in single thread mode
            else:
                self.resource_size = int(response.headers["Content-Length"])
        except Exception as e:
            print(e)

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

    def __pre_allocate_space(self):
        print(f"allocating: {self.resource_size} bytes")
        with open(self.resource_file_name, "wb") as out_file:
            # out_file.seek(self.resource_size - 1)
            # out_file.write(b"\0")
            os.truncate(out_file.fileno(), self.resource_size)

    def __download_part(self, start_byte, end_byte):
        print(f"downloading part from byte {start_byte} - byte {end_byte}")
        headers = {"Range": f"bytes={start_byte}-{end_byte}"}
        response = requests.get(
            url=self.resource_location_url,
            headers=headers,
            stream=True,
        )
        response.raise_for_status()
        with open(self.resource_file_name, "r+b") as out_file:
            out_file.seek(start_byte)
            for chunk in response.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    out_file.write(chunk)
        return response.status_code

    def download_resource(self):
        max_retries = 3
        pending = list(self.part_byte_ranges)

        for attempt in range(max_retries):
            if not pending:
                break
            failed = []
            with ThreadPoolExecutor(max_workers=self.number_of_threads) as executor:
                future_to_range = {
                    executor.submit(self.__download_part, start, end): (start, end) for start, end in pending
                }
                for future in as_completed(future_to_range):
                    byte_range = future_to_range[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f"ERROR - Part {byte_range} failed (attempt {attempt + 1}): {e}")
                        failed.append(byte_range)
            pending = failed

        if pending:
            raise RuntimeError(f"Parts failed after {max_retries} attempts: {pending}")

    def validate_resource_md5(self):
        with open(self.resource_file_name, "rb") as f:
            md5_hash = hashlib.md5(f.read()).hexdigest()
        if self.resource_md5:
            if md5_hash == self.resource_md5:
                print("md5 match, good download")
                return True
            else:
                print("md5 mismatch, bad download")
                print(md5_hash)
                return False
        else:
            print("no md5 provided, skipping verification")
            print(md5_hash)
