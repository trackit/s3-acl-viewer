#! /usr/bin/env python3

import argparse
import threading
import s3
from oauth2client import tools

import build_csv
import build_gspread
import build_xlsx
import build_print


def parse_args():
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument("-p", "--profile", help="aws profiles. [default] by default.", nargs='*', default=["default"])
    parser.add_argument("-n", "--name", help="spreadsheet name. [s3_report] by default.", default="s3_report")
    parser.add_argument("-g", "--gspread", help="create a google spreadsheet.", action="store_true")
    parser.add_argument("-x", "--xlsx", help="create a xlsx spreadsheet.", action="store_true")
    parser.add_argument("-c", "--csv", help="create a csv file.", action="store_true")
    parser.add_argument("-s", "--silent", help="disable printing.", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    buckets = [
        bucket
        for profile in args.profile
        for bucket in s3.fetch_profile(profile)
    ]

    c_threads = []
    if args.csv:
        c_threads += [threading.Thread(target=build_csv.build, args=(args.name, buckets))]
    if args.gspread:
        c_threads += [threading.Thread(target=build_gspread.build, args=(args.name, buckets, args))]
    if args.xlsx:
        c_threads += [threading.Thread(target=build_xlsx.build, args=(args.name, buckets))]
    if not args.silent:
        c_threads += [threading.Thread(target=build_print.build, args=([buckets]))]

    for c_thread in c_threads:
        c_thread.start()
    for c_thread in c_threads:
        c_thread.join()

if __name__ == "__main__":
    main()
