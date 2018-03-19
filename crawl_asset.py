import glob

asset_total_list = []
liability_total_list = []

for filename in glob.glob("*.txt"):
    file_handle = open(filename, encoding="utf-8")
    content = file_handle.readlines()
    content = filter(None, [x.strip() for x in content])
    asset_list = []
    liability_list = []
    asset_line = False
    liability_line = False
    line_cnt = 0

    for line in content:
        upper_line = line.upper().strip()

        if upper_line[0:25] == "STATEMENT OF NET POSITION":
            line_cnt = 80
            asset_line = 0
            liability_line = 0

        if line_cnt > 0:
            line_cnt = line_cnt - 1
            if line.rstrip() and not any(u_line_char.isdigit() for u_line_char in upper_line[0:50]):

                # ASSETS
                if (line[0:6].strip() == "ASSETS" or line[0:6] == "Assets") \
                        and ("ASSETS" and "YEARS") not in upper_line:
                    asset_line = True
                    liability_line = False

                if upper_line[0:35] == "TOTAL CURRENT NON-RESTRICTED ASSETS" or "TOTAL ASSETS" in upper_line[0:12] \
                        or upper_line[0:30] == "DEFERRED OUTFLOWS OF RESOURCES" or 'TOTAL ASSETS' in upper_line \
                        or 'TOTAL LIABILITIES' in upper_line or upper_line[0:11] == "LIABILITIES" \
                        or upper_line[0:4] == "CITY" or upper_line[0:20] == "TOTAL CAPITAL ASSETS" \
                        or line[0:11] == "Assets that" or line[0:13] == "Liabilities –" \
                        or line[0:22] == "The accompanying notes" or line[0:22] == "See accompanying notes" \
                        or line[0:10] == 'Assets and' or upper_line[0:15] == "ASSETS ACQUIRED" \
                        or upper_line[0:14] == "CAPITAL ASSETS":
                    asset_line = False

                # LIABILITIES
                if upper_line[0:20] == "CURRENT LIABILITIES:" or upper_line[0:20] == "CURRENT LIABILITIES " \
                        or line[0:11] == "Liabilities" or line[0:11] == "LIABILITIES":
                    liability_line = True
                    asset_line = False

                if upper_line[0:18] == "PRIMARY GOVERNMENT" or upper_line[0:29] == "DEFERRED INFLOWS OF RESOURCES" \
                        or upper_line[0:12] == "FUND BALANCE" \
                        or upper_line[0:30] == "DEFERRED OUTFLOWS OF RESOURCES" or upper_line[0:12] == "NET POSITION" \
                        or upper_line[0:17] == "TOTAL LIABILITIES" \
                        or upper_line[0:4] == "CITY" or upper_line[0:19] == "STATISTICAL SECTION" \
                        or line[0:22] == "The accompanying notes" or line[0:22] == "See accompanying notes" \
                        or line[0:15] == "Liabilities for" or line[0:13] == "Liabilities –" \
                        or line[0:20] == "STATEMENT OF CHANGES" or "Long-term liabilities" in line \
                        or "All liabilities" in line:
                    liability_line = False

                # INSERT

                if asset_line:
                    if len(line.strip()) > 0 and 'TOTAL' not in upper_line:
                        if upper_line[0:6] == "ASSETS":
                            asset_list.append("ASSETS")
                        else:
                            line = line.replace('$', '').replace('& ', 'and ')\
                                .replace('‐', '').replace(',', '')\
                                .replace('.', '').replace('(', '')\
                                .replace('—', '').replace(')', '').replace('-', '').strip()
                            line = ''.join([i for i in line[0:50] if not i.isdigit()])
                            asset_list.append(line.strip())

                if liability_line:
                    if len(line.strip()) > 0 and 'TOTAL' not in upper_line:
                        if upper_line[0:11] == "LIABILITIES":
                            liability_list.append("LIABILITIES")
                        else:
                            line = line.replace('$', '').replace('& ', 'and ')\
                                .replace('‐', '').replace('…', '')\
                                .replace(',', '').replace('.', '')\
                                .replace('(', '').replace('—', '')\
                                .replace(')', '').replace('-', '').strip()
                            line = ''.join([i for i in line[0:50] if not i.isdigit()])
                            liability_list.append(line.strip())
    seen = set()
    seen_add = seen.add
    asset_list = [asset for asset in asset_list if not (asset.lower() in seen or seen_add(asset.lower()))]
    liability_list = [liability for liability in liability_list if not (liability.lower() in seen
                                                                        or seen_add(liability.lower()))]
    asset_total_list.extend(asset_list)
    liability_total_list.extend(liability_list)

total_seen = set()
total_seen_add = total_seen.add

asset_total_list = [asset + ':' + str(asset_total_list.count(asset)) for asset in asset_total_list
                    if not (asset.lower() in total_seen or total_seen_add(asset.lower()))]
liability_total_list = [liability + ':' + str(liability_total_list.count(liability))
                        for liability in liability_total_list if not (liability.lower() in total_seen
                                                                      or total_seen_add(liability.lower()))]

for asset_content in asset_total_list:
    print(asset_content)

for liability_content in liability_total_list:
    print(liability_content)
