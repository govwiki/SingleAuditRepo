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

    crawler = Crawler(config, 'revenues')
    crawler.get(config.get('revenues', 'url'))

    revenue_total_list = []
    expenditure_total_list = []

    for row in crawler.get_elements('tbody tr'):
        items = crawler.get_elements('td', root=row)
        filename = items[0].text
        print("Current Filename is {}".format(filename))
        url = crawler.get_attr('a', 'href', root=items[0])
        crawler.download(url, filename)

        convert_filename = filename.replace('.pdf', '.txt')
        os.system("pdftotext '%s' '%s'" % (downloads_path + 'Revenues/' + filename,
                                           downloads_path + 'Revenues/' + convert_filename))
        file_handle = open(downloads_path + 'Revenues/' + convert_filename, encoding="utf-8")
        content = file_handle.readlines()
        content = list(filter(None, [x.strip() for x in content]))

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
                line_cnt = 30

            if line_cnt > 0:
                line_cnt = line_cnt - 1

                if "TOTAL EXPENDITURE" in upper_line:
                    break

                # REVENUES
                if upper_line[0:8] == "REVENUES":
                    revenue_line = True
                    expenditure_line = False

                if upper_line[0:13] == "TOTAL REVENUE":
                    revenue_line = False

                # EXPENDITURES
                if upper_line[0:12] == "EXPENDITURES":
                    revenue_line = False
                    expenditure_line = True

                # INSERT
                if revenue_line:
                    if len(line.strip()) > 0 and 'TOTAL' not in upper_line \
                            and not any(u_line_char.isdigit() for u_line_char in upper_line[0:50]) \
                            and not upper_line[0:8] == "REVENUES":
                        revenue_list.append(str(line[0:50]).replace('& ', 'and ')
                                            .replace('', ' ').replace('-', '').replace(':', '')
                                            .replace('$', '').replace('—', '').replace('*', '')
                                            .replace('…', '').replace('.', '').lower().strip())

                if expenditure_line:
                    if len(line.strip()) > 0 and 'TOTAL' not in upper_line \
                            and not any(u_line_char.isdigit() for u_line_char in upper_line[0:50]) \
                            and not upper_line[0:12] == "EXPENDITURES":
                        expenditure_list.append(str(line[0:50]).replace('& ', 'and ').replace(':', '')
                                                .replace('', ' ').replace('-', '').replace('*', '')
                                                .replace('$', '').replace('—', '')
                                                .replace('…', '').replace('.', '').lower().strip())

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

    with open(downloads_path + 'Revenues/rev&exp_output.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(["Revenue Name", "Count"])
        for revenue in revenue_total_list:
            if not revenue == "revenues":
                revenue_name = revenue.split(':')[0]
                count = revenue.split(':')[1]
                writer.writerow([revenue_name, count])

        writer.writerow(["", ""])
        writer.writerow(["Expenditure Name", "Count"])
        for expenditure in expenditure_total_list:
            if not expenditure == "expenditures":
                expenditure_name = expenditure.split(':')[0]
                count = expenditure.split(':')[1]
                writer.writerow([expenditure_name, count])

    print("Done")

    csv_file.close()
    crawler.close()
