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



def build(name, buckets):
    workbook = xlsxwriter.Workbook("{}.xlsx".format(name))
    worksheet = workbook.add_worksheet(name)
    worksheet.hide_gridlines(2)

    write_header(workbook, worksheet)
    write_data(workbook, worksheet, buckets)

    workbook.close()

if __name__ == "__main__":
    import s3
    build("test.xlsx", [
        s3.Bucket("hey")
        for _ in range(10)
    ])
