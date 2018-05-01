import configparser
import os
import sys
import csv
from utils import Crawler
from PyPDF2 import PdfFileReader
import sys
import textract

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'assets')
    crawler.get(config.get('assets', 'url'))

    asset_total_list = []
    liability_total_list = []

    for row in crawler.get_elements('tbody tr'):
        items = crawler.get_elements('td', root=row)
        filename = items[0].text
        print("Current Filename is {}".format(filename))
        url = crawler.get_attr('a', 'href', root=items[0])
        crawler.download(url, filename)

        convert_filename = filename.replace('.pdf', '.txt')
        os.system("pdftotext '%s' '%s'" % (downloads_path + 'Assets/' + filename,
                                           downloads_path + 'Assets/' + convert_filename))
        file_handle = open(downloads_path + 'Assets/' + convert_filename, encoding="utf-8")
        content = file_handle.readlines()
        content = list(filter(None, [x.strip() for x in content]))

        asset_list = []
        liability_list = []
        asset_line = False
        liability_line = False
        line_cnt = 0

        for line in content:
            upper_line = line.upper().strip()

            if upper_line[0:25] == "STATEMENT OF NET POSITION":
                index = content.index(line)
                upper_next_line = content[int(index+1)].upper().strip()
                if upper_next_line[0:18] == "SEPTEMBER 30, 2016":
                    line_cnt = 30
                    asset_line = 0
                    liability_line = 0

            if line_cnt > 0:
                line_cnt = line_cnt - 1
                if line.rstrip() and not any(u_line_char.isdigit() for u_line_char in upper_line[0:50]):

                    if upper_line[0:17] == "TOTAL LIABILITIES":
                        break

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
                        if len(line.strip()) > 0 and 'TOTAL' not in upper_line and not upper_line[0:5] == 'ASSET':
                            line = line.replace('$', '').replace('& ', 'and ')\
                                .replace('‐', '').replace(',', '')\
                                .replace('.', '').replace('(', '')\
                                .replace('—', '').replace(')', '').replace('-', '').strip()
                            line = ''.join([i for i in line[0:50] if not i.isdigit()])
                            asset_list.append(line.lower().strip())

                    if liability_line:
                        if len(line.strip()) > 0 and 'TOTAL' not in upper_line and not upper_line[0:8] == 'LIABILIT':
                            line = line.replace('$', '').replace('& ', 'and ')\
                                .replace('‐', '').replace('…', '')\
                                .replace(',', '').replace('.', '')\
                                .replace('(', '').replace('—', '')\
                                .replace(')', '').replace('-', '').strip()
                            line = ''.join([i for i in line[0:50] if not i.isdigit()])
                            liability_list.append(line.lower().strip())
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

    with open(downloads_path + 'Assets/ass&lia_output.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(["Asset Name", "Count"])
        for asset in asset_total_list:
            if '-' not in asset:
                asset_name = asset.split(':')[0]
                count = asset.split(':')[1]
                writer.writerow([asset_name, count])

        writer.writerow(["", ""])
        writer.writerow(["Liability Name", "Count"])
        for liability in liability_total_list:
            if '-' not in liability:
                liability_name = liability.split(':')[0]
                count = liability.split(':')[1]
                writer.writerow([liability_name, count])

    print("Done")

    csv_file.close()
    crawler.close()
