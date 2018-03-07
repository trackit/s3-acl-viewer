from termcolor import colored

def build(buckets):
    for bucket in buckets:
        print("-"*60, end="\n\n")
        print("Profile: {}".format(bucket.profile))
        print("Bucket: {}".format(colored(bucket.name, "blue", attrs=["bold"])))
        safe = True
        msg = []
        for perm in bucket.permission.keys():
            for p in ("READ", "WRITE", "READ_ACP", "WRITE_ACP", "FULL_CONTROL"):
                if bucket.permission[perm][p]:
                    safe = False
                    msg += ["  - {} by {}!".format(colored(p, "red"), colored(perm, "red"))]
        if not safe:
            print("{}:".format(colored("Vulnerabilities", "red", attrs=["bold"])))
            print("\n".join(msg))
        print("Your bucket is {}!".format(
            colored("safe", "green", attrs=["bold"]) if safe else
            colored("NOT safe", "red", attrs=["bold"])),
            end="\n\n")
    print("-"*60)
