import csv

def build(name, buckets):
    with open("{}.csv".format(name), "w", newline="") as csvfile:
        fieldnames = [
            "Account", "Bucket",
            "(Public) Read", "(Public) Write",
            "(Public) Read ACL", "(Public) Write ACL",
            "(Public) Full Control",
            "(Authenticated AWS users) Read", "(Authenticated AWS users) Write",
            "(Authenticated AWS users) Read ACL", "(Authenticated AWS users) Write ACL",
            "(Authenticated AWS users) Full Control",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for bucket in buckets:
            writer.writerow(bucket.dump_csv())
    with open("{}.csv".format(name + "_policy"), "w", newline="") as csvfile:
        fieldnames = [
            "Principal", "Action", "Effect", "Resources",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for bucket in buckets:
            for policies in bucket.policy:
                writer.writerow(policies)
