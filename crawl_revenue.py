import glob

revenue_total_list = []
expenditure_total_list = []

for filename in glob.glob("*.txt"):
    file_handle = open(filename, encoding="utf-8")
    content = file_handle.readlines()
    content = filter(None, [x.strip() for x in content])
    revenue_list = []
    expenditure_list = []
    revenue_line = False
    expenditure_line = False
    line_cnt = 0

    for line in content:
        upper_line = line.upper().strip()

        if "STATEMENT OF REVENUES, EXPENDITURES" in upper_line:
            revenue_line = False
            expenditure_line = False
            line_cnt = 50

        if line_cnt > 0:
            line_cnt = line_cnt - 1
            if line.rstrip():

                # REVENUES
                if upper_line[0:8] == "REVENUES":
                    revenue_line = True
                    expenditure_line = False

                if upper_line[0:13] == "TOTAL REVENUE" \
                        or line[0:14] == "Totalrevenues" or upper_line[0:9] == "EXPENSES:" \
                        or upper_line[0:6] == "EXCESS" \
                        or upper_line[0:16] == "REVENUES INCLUDE" or line[0:22] == "The accompanying notes" \
                        or line[0:22] == "See accompanying notes" or "REVENUES." in upper_line \
                        or upper_line[0:11] == "REVENUES IN" \
                        or upper_line[0:18] == "REVENUES & SOURCES" or "OTHER FINANCING SOURCES" in upper_line \
                        or upper_line[0:24] == "REVENUES AND RECEIVABLES" or upper_line[0:12] == "REVENUES ARE" \
                        or upper_line[0:12] == "FUND BALANCE" or upper_line[0:30] == "TO THE STATEMENT OF ACTIVITIES" \
                        or line[0:8] == "revenues" or upper_line[0:19] == "REVENUES RECOGNIZED" \
                        or upper_line[0:14] == "REVENUES OTHER" or upper_line[0:26] == "NET CHANGE IN FUND BALANCE" \
                        or "GENERAL EMPLOYEES' PENSION PLAN" in upper_line or upper_line[0:12] == "REVENUES NOT" \
                        or "(CONTINUED)" in upper_line or upper_line[0:16] == "THE NOTES TO THE" \
                        or upper_line[0:9] == "EMERGENCY" or upper_line[0:4] == "TAKE" \
                        or upper_line[0:11] == "EM TRAINING" or upper_line[0:7] == "SHERIFF" \
                        or upper_line[0:14] == "CAPITAL ASSETS" \
                        or upper_line[0:13] == "REVENUES THAT" or upper_line[0:15] == "REVENUES EARNED" \
                        or upper_line[0:14] == "REVENUES WHICH" or upper_line[0:26] == "REVENUES AND OTHER SOURCES" \
                        or upper_line[0:22] == "SEE ACCOMPANYING NOTES" or "PROVIDE" in upper_line \
                        or upper_line[0:17] == "REVENUES CAPACITY" or upper_line[0:20] == "OTHER FINANCING USES" \
                        or upper_line[0:24] == "BALANCE TO THE STATEMENT":
                    revenue_line = False

                # EXPENDITURES
                if upper_line[0:12] == "EXPENDITURES":
                    revenue_line = False
                    expenditure_line = True

                if upper_line[0:18] == "TOTAL EXPENDITURES" or line[0:18] == "Totalexpenditures" or \
                        upper_line[0:6] == "EXCESS" \
                        or upper_line[0:8] == "EXPENSES" or line[0:14] == "Total expenses" \
                        or "See Auditors'" in line or line[0:20] == "(TOTAL EXPENDITURES)" \
                        or "other financing sources" in line.lower() or "(CONTINUED)" in upper_line \
                        or line[0:22] == "The accompanying notes" \
                        or line[0:22] == "See accompanying notes" or upper_line[0:13] == "EXPENDITURES," \
                        or upper_line[0:15] == "EXPENDITURES OF" \
                        or upper_line[0:16] == "EXPENDITURES FOR" or upper_line[0:13] == "EXPENDITURES." \
                        or upper_line[0:15] == "EXPENDITURES IN" or upper_line[0:17] == "EXPENDITURES OVER" \
                        or line[0:11] == "expenditure" or "FUND BALANCE TO THE" in upper_line \
                        or upper_line[0:12] == "FUND BALANCE" or "FUND BALANCES OF" in upper_line \
                        or "FUND BALANCES-BUDGET" in upper_line or "EXPENDITURES MAY" in upper_line \
                        or upper_line[0:12] == "(DEFICIENCY)" or upper_line[0:26] == "NET CHANGE IN FUND BALANCE" \
                        or "GENERAL EMPLOYEES' PENSION PLAN" in upper_line or upper_line[0:16] == "THE NOTES TO THE" \
                        or upper_line[0:9] == "EMERGENCY" or upper_line[0:4] == "TAKE" \
                        or upper_line[0:11] == "EM TRAINING" or upper_line[0:7] == "SHERIFF" \
                        or upper_line[0:14] == "CAPITAL ASSETS" \
                        or upper_line[0:16] == "EXPENDITURES ARE" or upper_line[0:22] == "EXPENDITURES GENERALLY" \
                        or upper_line[0:22] == "SEE ACCOMPANYING NOTES" or upper_line[0:22] == "DEFICIENCY OF REVENUES" \
                        or upper_line[0:20] == "OTHER FINANCING USES" or "RECONCILES" in upper_line \
                        or upper_line[0:15] == "BUDGETARY BASIS" or upper_line[0:4] == "GAAP":
                    expenditure_line = False

                # INSERT
                if revenue_line:
                    if len(line.strip()) > 0 and 'TOTAL' not in upper_line \
                            and not any(u_line_char.isdigit() for u_line_char in upper_line[0:50]):
                        if upper_line[0:8] == "REVENUES":
                            revenue_list.append("REVENUES")
                        else:
                            revenue_list.append(str(line[0:50]).replace('& ', 'and ')
                                                .replace('', ' ').replace('-', '')
                                                .replace('$', '').replace('—', '')
                                                .replace('…', '').replace('.', '').strip())

                if expenditure_line:
                    if len(line.strip()) > 0 and 'TOTAL' not in upper_line \
                            and not any(u_line_char.isdigit() for u_line_char in upper_line[0:50]):
                        if upper_line[0:12] == "EXPENDITURES":
                            expenditure_list.append("EXPENDITURES")
                        else:
                            expenditure_list.append(str(line[0:50]).replace('& ', 'and ')
                                                    .replace('', ' ').replace('-', '')
                                                    .replace('$', '').replace('—', '')
                                                    .replace('…', '').replace('.', '').strip())

    seen = set()
    seen_add = seen.add
    revenue_list = [revenue for revenue in revenue_list if not (revenue.lower() in seen or seen_add(revenue.lower()))]
    expenditure_list = [expenditure for expenditure in expenditure_list
                        if not (expenditure.lower() in seen or seen_add(expenditure.lower()))]
    revenue_total_list.extend(revenue_list)
    expenditure_total_list.extend(expenditure_list)

total_seen = set()
total_seen_add = total_seen.add

revenue_total_list = [revenue + ':' + str(revenue_total_list.count(revenue)) for revenue in revenue_total_list
                      if not (revenue.lower() in total_seen or total_seen_add(revenue.lower()))]
expenditure_total_list = [expenditure + ':' + str(expenditure_total_list.count(expenditure))
                          for expenditure in expenditure_total_list if not (expenditure.lower() in total_seen
                                                                            or total_seen_add(expenditure.lower()))]

for revenue_content in revenue_total_list:
    print(revenue_content)

for expenditure_content in expenditure_total_list:
    print(expenditure_content)
