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

    crawler = Crawler(config, 'captions')
    crawler.get(config.get('captions', 'url'))

    captions_list = []

    for row in crawler.get_elements('tbody tr'):
        items = crawler.get_elements('td', root=row)
        filename = items[0].text
        print("Current Filename is {}".format(filename))
        url = crawler.get_attr('a', 'href', root=items[0])
        crawler.download(url, filename)

        convert_filename = filename.replace('.pdf', '.txt')
        os.system("pdftotext '%s' '%s'" % (downloads_path + 'Captions/' + filename,
                                           downloads_path + 'Captions/' + convert_filename))
        file_handle = open(downloads_path + 'Captions/' + convert_filename, encoding="utf-8")
        content = file_handle.readlines()
        content = list(filter(None, [x.strip() for x in content]))

        line_cnt = 0
        caption_line = False

        for line in content:
            upper_line = line.upper().strip()
            if upper_line[0:28] == 'FOR THE YEAR ENDED SEPTEMBER':
                index = content.index(line)
                upper_prev_line = content[int(index-1)].upper().strip()
                if upper_prev_line[0:23] == "STATEMENT OF ACTIVITIES":
                    line_cnt = 20

            if line_cnt > 0:
                line_cnt = line_cnt - 1

                if 'PROGRAM' in upper_line:
                    caption_line = True

                if upper_line[0:24] == 'TOTAL PRIMARY GOVERNMENT':
                    break

                if line.isupper():
                    continue

                if caption_line:
                    upper_line = upper_line[0:50]
                    if len(line.strip()) > 0 and 'TOTAL' not in upper_line and 'FOR THE YEAR' not in upper_line \
                            and '$' not in upper_line and 'ACTIVITIES' not in upper_line and 'PROGRAM' not in upper_line \
                            and 'EXPENSE' not in upper_line and ':' not in upper_line \
                            and not any(u_line_char.isdigit() for u_line_char in upper_line[0:50]) \
                            and 'CHARGES' not in upper_line and not upper_line[0:8] == 'SERVICES' \
                            and 'REVENUE' not in upper_line and 'ASSET' not in upper_line and 'CITY' not in upper_line \
                            and 'TOWN' not in upper_line and 'COUNTY' not in upper_line \
                            and 'TABLE OF CONTENTS' not in upper_line and '(' not in upper_line:
                        captions_list.append(str(line[0:50]).replace('& ', 'and ')
                                             .replace('*', '').replace('-', '')
                                             .replace('$', '').replace('—', '')
                                             .replace('…', '').replace('.', '').strip())

        os.remove(downloads_path + 'Captions/' + convert_filename)
        print("Removed {}".format(convert_filename))

    seen = set()
    seen_add = seen.add

    captions_list = [caption + ':' + str(captions_list.count(caption)) for caption in captions_list
                          if not (caption.lower() in seen or seen_add(caption.lower()))]

    with open(downloads_path + 'Captions/output_file.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(["Caption Name", "Count"])
        for caption in captions_list:
            if '-' not in caption:
                caption_name = caption.split(':')[0]
                count = caption.split(':')[1]
                writer.writerow([caption_name, count])

    print("Done")

    csv_file.close()
    crawler.close()
