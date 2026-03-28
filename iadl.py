import InternetArchive
import DownloadItem
import argparse


def setup_arg_parser():
    parser = argparse.ArgumentParser(description="Download items from Internet Archive")
    parser.add_argument("-u", "--url", type=str, required=True, help="URL of the item to download")
    parser.add_argument("-c", "--collection", type=str, required=True, help="Collection of the item")
    parser.add_argument("-e", "--email", type=str, help="Email for authentication")
    parser.add_argument("-p", "--password", type=str, help="Password for authentication")
    parser.add_argument("-s", "--s3_access_key", type=str, help="S3 access key for authentication")
    parser.add_argument("-k", "--s3_secret_key", type=str, help="S3 secret key for authentication")
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of download threads")

    return parser


def main():
    parser = setup_arg_parser()
    args = parser.parse_args()

    ia = InternetArchive.InternetArchive(
        url=args.url, collection=args.collection, email=args.email, password=args.password
    )


if __name__ == "__main__":
    main()
