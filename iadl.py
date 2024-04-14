import InternetArchive
import DownloadItem
import argparse


def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest="command")
    sub_parsers.required = True

    parser_1 = sub_parsers.add_parser("download", help="download an item")
    parser_1.add_argument("-f", "--file", action="store_true")
    parser_1.add_argument("-s", "--sac", type=str, help="")
    args = parser.parse_args()

    if args.command == "download":
        pass


if __name__ == "__main__":
    main()
