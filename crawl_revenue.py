revenue_list = []
expenditure_list = []
state = False

with open("FL Alachua County 2016.txt", 'rb') as file_handle:
    content = file_handle.readlines()
    content = filter(None, [x.strip() for x in content])
    revenue_line = False
    expenditure_line = False

    for line_num, line in enumerate(content):
        upper_line = line.upper().strip()

        if upper_line[0:35] == "STATEMENT OF REVENUES, EXPENDITURES":
            state = True

        if state:
            if line.rstrip() and not any(u_line_char.isdigit() for u_line_char in upper_line):
                if line[0:8] == "REVENUES":
                    revenue_line = True

                if upper_line[0:13] == "TOTAL REVENUE" or line[0:14] == "Totalrevenues":
                    revenue_line = False

                if line[0:12] == "EXPENDITURES":
                    expenditure_line = True

                if upper_line[0:18] == "TOTAL EXPENDITURES" or line[0:18] == "Totalexpenditures":
                    expenditure_line = False

                if revenue_line:
                    if len(line.strip()) > 0:
                        if not line[0:8] == "REVENUES" and ":" not in line and not line[0:7] == "Current":
                            revenue_list.append(str(line[0:50]).replace('and', '&').replace('', ' '))

                if expenditure_line:
                    if len(line.strip()) > 0:
                        if not line[0:12] == "EXPENDITURES" and ":" not in line and not line[0:7] == "Current":
                            expenditure_list.append(str(line[0:50]).replace('and', '&').replace('', ' '))

    seen = set()
    seen_add = seen.add
    print '\n'
    print 'Revenues:'
    revenue_list = [revenue + ':' + str(revenue_list.count(revenue)) for revenue in revenue_list
                    if not (revenue in seen or seen_add(revenue))]
    for revenue_content in revenue_list:
        print revenue_content
    print '\n'

    print 'Expenditures:'
    expenditure_list = [expenditure + ':' + str(expenditure_list.count(expenditure)) for expenditure in expenditure_list
                        if not (expenditure in seen or seen_add(expenditure))]
    for expenditure_content in expenditure_list:
        print expenditure_content
