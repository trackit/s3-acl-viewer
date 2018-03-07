import boto3
import json
import datetime
import threading
from collections import defaultdict

GROUPS_TO_CHECK = {
    "http://acs.amazonaws.com/groups/global/AllUsers": "Everyone",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers": "Authenticated AWS users"
}

class Bucket:
    tr_yn = lambda x: "Y" if x else "N"

    def __init__(self, name, profile=None, creation_date=None):
        self.name = name
        self.creation_data = creation_date
        self.profile = profile
        self.permission = {
            "Everyone": defaultdict(bool),
            "Authenticated AWS users": defaultdict(bool),
        }

    def add_perm(self, who, what):
        self.permission[who][what] = True

    def add_profile(self, profile):
        self.profile = profile

    def dump_csv(self):
        return {
            'Account': self.profile,
            'Bucket': self.name,
            '(Public) Read': Bucket.tr_yn(self.permission["Everyone"]["READ"]),
            '(Public) Write': Bucket.tr_yn(self.permission["Everyone"]["WRITE"]),
            '(Public) Read ACL': Bucket.tr_yn(self.permission["Everyone"]["READ_ACP"]),
            '(Public) Write ACL': Bucket.tr_yn(self.permission["Everyone"]["WRITE_ACP"]),
            '(Public) Full Control': Bucket.tr_yn(self.permission["Everyone"]["FULL_CONTROL"]),
            '(Authenticated AWS users) Read': Bucket.tr_yn(self.permission["Authenticated AWS users"]["READ"]),
            '(Authenticated AWS users) Write': Bucket.tr_yn(self.permission["Authenticated AWS users"]["WRITE"]),
            '(Authenticated AWS users) Read ACL': Bucket.tr_yn(self.permission["Authenticated AWS users"]["READ_ACP"]),
            '(Authenticated AWS users) Write ACL': Bucket.tr_yn(self.permission["Authenticated AWS users"]["WRITE_ACP"]),
            '(Authenticated AWS users) Full Control': Bucket.tr_yn(self.permission["Everyone"]["FULL_CONTROL"]),
        }

    def dump_xlsx(self):
        d = self.dump_csv()
        return [
            d["Account"],
            d["Bucket"],
            d["(Public) Read"],
            d["(Public) Write"],
            d["(Public) Read ACL"],
            d["(Public) Write ACL"],
            d["(Public) Full Control"],
            d["(Authenticated AWS users) Read"],
            d["(Authenticated AWS users) Write"],
            d["(Authenticated AWS users) Read ACL"],
            d["(Authenticated AWS users) Write ACL"],
            d["(Authenticated AWS users) Full Control"]
        ]

    def dump_gspread(self):
        return self.dump_csv()


def fetch_acl(s3_client, bucket):
    acl = s3_client.get_bucket_acl(Bucket=bucket.name)
    for grant in acl["Grants"]:
        if "Grantee" in grant \
            and "URI" in grant["Grantee"] \
            and grant["Grantee"]["URI"] in GROUPS_TO_CHECK:
            bucket.add_perm(
                GROUPS_TO_CHECK[grant["Grantee"]["URI"]],
                grant["Permission"]
            )


def fetch_buckets(s3_client):
    return [
        Bucket(bucket["Name"], bucket["CreationDate"])
        for bucket in s3_client.list_buckets()["Buckets"]
    ]

def fetch_profile(profile):
    try:
        session = boto3.Session(profile_name=profile)
        s3 = session.resource("s3")
        s3_client = session.client("s3")
        buckets = fetch_buckets(s3_client)
    except Exception as e:
        print("Fatal error for the profile {}".format(profile))
        print(e)
        exit(1)

    for i in range(len(buckets)):
        buckets[i].add_profile(profile)
        buckets[i].thread = threading.Thread(target=fetch_acl, args=(s3_client, buckets[i]))
        buckets[i].thread.setDaemon(True)
        buckets[i].thread.start()

    for bucket in buckets:
        bucket.thread.join()

    return buckets

