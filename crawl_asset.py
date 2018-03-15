asset_list = []
liability_list = []
state = False

with open("FL Alachua County 2016.txt", 'rb') as file_handle:
    content = file_handle.readlines()
    content = filter(None, [x.strip() for x in content])
    asset_line = False
    liability_line = False

    for line_num, line in enumerate(content):
        upper_line = line.upper().strip()

        if upper_line[0:25] == "STATEMENT OF NET POSITION":
            state = True

        if state:
            if line.rstrip() and not any(u_line_char.isdigit() for u_line_char in upper_line):
                if upper_line[0:14] == "CURRENT ASSETS":
                    asset_line = True

                if upper_line[0:35] == "TOTAL CURRENT NON-RESTRICTED ASSETS" or "TOTAL CURRENT ASSETS" in upper_line:
                    asset_line = False

                if upper_line[0:20] == "CURRENT LIABILITIES:" or upper_line[0:20] == "CURRENT LIABILITIES ":
                    liability_line = True

                if upper_line[0:18] == "PRIMARY GOVERNMENT" or upper_line[0:29] == "DEFERRED INFLOWS OF RESOURCES" \
                        or "total current liabilities" in upper_line.lower():
                    liability_line = False

                if asset_line:
                    if len(line.strip()) > 0:
                        if 'current assets' not in line[0:50].lower() and ':' not in line:
                            asset_list.append(str(line[0:50]).replace('and', '&'))

                if liability_line:
                    if len(line.strip()) > 0:
                        if 'current liabilities' not in line[0:50].lower() and not line[0:11].lower() == 'liabilities':
                            liability_list.append(str(line[0:50]).replace('and', '&'))

    seen = set()
    seen_add = seen.add
    print '\n'
    print 'Assets:'
    asset_list = [asset + ':' + str(asset_list.count(asset)) for asset in asset_list
                  if not (asset in seen or seen_add(asset))]
    for asset_content in asset_list:
        print asset_content
    print '\n'

    print 'Liabilities:'
    liability_list = [liability + ':' + str(liability_list.count(liability)) for liability in liability_list
                      if not (liability in seen or seen_add(liability))]
    for liability_content in liability_list:
        print liability_content
