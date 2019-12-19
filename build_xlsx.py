import xlsxwriter

def write_header(workbook, worksheet):
    header_format = workbook.add_format()
    header_format.set_bold()
    header_format.set_align("center")
    header_format.set_align("vcenter")
    header_format.set_border()

    worksheet.set_column("A:A", 25)
    worksheet.set_column("B:B", 60)
    worksheet.set_column("C:L", 15)

    worksheet.merge_range("A1:A2", "Account", header_format)
    worksheet.merge_range("B1:B2", "Bucket", header_format)
    worksheet.merge_range("C1:G1", "Public", header_format)
    worksheet.write("C2", "Read", header_format)
    worksheet.write("D2", "Write", header_format)
    worksheet.write("E2", "Read ACL", header_format)
    worksheet.write("F2", "Write ACL", header_format)
    worksheet.write("G2", "Full Control", header_format)
    worksheet.merge_range("H1:L1", "Authenticated AWS users", header_format)
    worksheet.write("H2", "Read", header_format)
    worksheet.write("I2", "Write", header_format)
    worksheet.write("J2", "Read ACL", header_format)
    worksheet.write("K2", "Write ACL", header_format)
    worksheet.write("L2", "Full Control", header_format)
    

def write_data(workbook, worksheet, buckets):
    data_format = workbook.add_format()
    data_format.set_border()
    data_format.set_align("center")
    data_format.set_align("vcenter")

    i = 2
    for bucket in buckets:
        j = 0
        for d in bucket.dump_xlsx():
            worksheet.write(i, j, d, data_format)
            j += 1
        i += 1

    red = workbook.add_format()
    red.set_bg_color("#ff948a")
    red.set_bold()
    green = workbook.add_format()
    green.set_bg_color("#b7e1cd")
    worksheet.conditional_format(2, 2, i, 11, {
        "type":     "text",
        "criteria": "containing",
        "value":    "N",
        "format":   green,
    })
    worksheet.conditional_format(2, 2, i, 11, {
        "type":     "text",
        "criteria": "containing",
        "value":    "Y",
        "format":   red,
    })


def write_header_policies(workbook, worksheet):
    header_format = workbook.add_format()
    header_format.set_bold()
    header_format.set_align("center")
    header_format.set_align("vcenter")
    header_format.set_border()

    worksheet.set_column("A:A", 45)
    worksheet.set_column("B:B", 25)
    worksheet.set_column("C:C", 10)
    worksheet.set_column("D:D", 45)
    worksheet.set_column("E:E", 20)
    worksheet.set_column("F:F", 100)
    worksheet.merge_range("E1:F1", "Principal", header_format)
    worksheet.write("B1", "Actions", header_format)
    worksheet.write("C1", "Effect", header_format)
    worksheet.write("D1", "Resources", header_format)
    worksheet.write("A1", "S3 Buckets", header_format)


def format_sheet(worksheet, workbook, line):
    red = workbook.add_format()
    red.set_bg_color("#ff948a")
    red.set_bold()
    green = workbook.add_format()
    green.set_bg_color("#b7e1cd")
    worksheet.conditional_format(1, 1, line, 11, {
        "type":     "text",
        "criteria": "containing",
        "value":    "Deny",
        "format":   green,
    })
    worksheet.conditional_format(1, 1, line, 11, {
        "type":     "text",
        "criteria": "containing",
        "value":    "Allow",
        "format":   red,
    })


def write_right_principal(worksheet, policies, data_format, i, color_format):
    worksheet.write("F" + str(i), "/", data_format)
    worksheet.write("F" + str(i + 1), "/", color_format)
    worksheet.write("F" + str(i + 2), "/", data_format)
    worksheet.write("F" + str(i + 3), "/", color_format)
    func_table = {
        "AWS": (data_format, i),
        "Service": (color_format, i + 1),
        "CanonicalUser": (data_format, i + 2),
        "Federated": (color_format, i + 3),
    }
    for principal_type in policies["Principal"]:
        format_type, line = func_table[principal_type]
        worksheet.write("F" + str(line), policies["Principal"][principal_type], format_type)


def get_format(workbook):
    data_format = workbook.add_format()
    data_format.set_border()
    data_format.set_align("center")
    data_format.set_align("vcenter")
    header_format = workbook.add_format()
    header_format.set_bold()
    header_format.set_align("center")
    header_format.set_align("vcenter")
    header_format.set_border()
    color_format_header = workbook.add_format()
    color_format_header.set_border()
    color_format_header.set_align("center")
    color_format_header.set_align("vcenter")
    color_format_header.set_bg_color('#d6d6d6')
    color_format_header.set_bold()
    color_format = workbook.add_format()
    color_format.set_border()
    color_format.set_align("center")
    color_format.set_align("vcenter")
    color_format.set_bg_color('#d6d6d6')
    return data_format, header_format, color_format_header, color_format


def write_data_policies(workbook, worksheet, buckets):
    data_format, header_format, color_format_header, color_format = get_format(workbook)

    line = 2
    merge_line = 2
    i = 0
    bucket_policy = False
    for bucket in buckets:
        for policies in bucket.policy:
            bucket_policy = True
            write_right_principal(worksheet, policies, data_format, line, color_format)
            worksheet.merge_range("B" + str(line) + ":B" + str(line + 3), policies["Action"], data_format)
            worksheet.merge_range("C" + str(line) + ":C" + str(line + 3), policies["Effect"], data_format)
            worksheet.merge_range("D" + str(line) + ":D" + str(line + 3), policies["Resources"], data_format)
            worksheet.write("E" + str(line), "AWS", header_format)
            worksheet.write("E" + str(line + 1), "Service", color_format_header)
            worksheet.write("E" + str(line + 2), "Canonical", header_format)
            worksheet.write("E" + str(line + 3), "Federated", color_format_header)
            line += 4
            i += 1
        if bucket_policy:
            worksheet.merge_range("A" + str(merge_line) + ":A" + str(line - 1), bucket.name, data_format)
            bucket_policy = False
        merge_line = line
    format_sheet(worksheet, workbook, line)



def build(name, buckets):
    workbook = xlsxwriter.Workbook("{}.xlsx".format(name))
    worksheet = workbook.add_worksheet(name)
    worksheet.hide_gridlines(2)

    write_header(workbook, worksheet)
    write_data(workbook, worksheet, buckets)

    worksheet2 = workbook.add_worksheet(name + "_policies")
    worksheet.hide_gridlines(2)

    write_header_policies(workbook, worksheet2)
    write_data_policies(workbook, worksheet2, buckets)

    workbook.close()

if __name__ == "__main__":
    import s3
    build("test.xlsx", [
        s3.Bucket("hey")
        for _ in range(10)
    ])
