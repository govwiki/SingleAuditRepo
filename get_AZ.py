import configparser
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'AZ'

    def _get_remote_filename(self, local_filename):
        entity_name, entity_type, year = local_filename[:-4].split('|')
        if entity_type == 'County':
            directory = 'General Purpose'
        else:
            directory = 'Community College Districts'
        filename = '{} {} {}.pdf'.format(self.abbr, entity_name, year)
        return directory, filename


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'arizona')
    entity_type = 'County'
    for state_url in config.get('arizona', 'urls').split('\n'):
        crawler.get(state_url.strip())
        while True:
            for row in crawler.get_elements('div.views-row'):
                row_type = crawler.get_text('.views-field-field-audit-type', root=row)
                if 'financial audit' in row_type.lower() or 'single audit' in row_type.lower():
                    url = crawler.get_attr('strong a', 'href', root=row)
                    if entity_type == 'County':
                        text = crawler.get_text('.views-field.views-field-field-counties', root=row)
                    else:
                        text = crawler.get_text('.views-field.views-field-field-community-college', root=row)
                    year = crawler.get_text('span[datatype="xsd:dateTime"]', root=row)[-4:]
                    crawler.download(url, '{}|{}|{}.pdf'.format(text, entity_type, year))
                    crawler.upload_to_ftp('{}|{}|{}.pdf'.format(text, entity_type, year))
            try:
                crawler.get(crawler.get_attr('.next a', 'href'))
            except Exception:
                break
        entity_type = 'Community College'
    crawler.close()
