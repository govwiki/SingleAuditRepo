import configparser
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'NY'

    def _get_remote_filename(self, local_filename):
        year, name = local_filename[:-4].split('|')
        name, _ = name.split(' (')
        name = name.split(' \x96 ')[0]
        entity_type = _[:-1]
        if entity_type in ('Town', 'City', 'Village'):
            name = name.split(' of ')[1]
            directory = 'General Purpose'
        elif entity_type == 'School':
            name = name.split('  ')[0]
            directory = 'School District'
        else:
            directory = 'Special District'
        return directory, '{} {} {}.pdf'.format(self.abbr, name, year)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'new_york')
    crawler.get(config.get('new_york', 'url'))

    for item in crawler.get_elements('#textContainer1>div')[1:]:
        url = crawler.get_attr('a', 'href', root=item)
        subitems = crawler.get_text('div', single=False, root=item)
        year = subitems[1].split(':')[-1].strip()
        name = subitems[3].split(':')[-1].strip()
        filename = '{}|{}.pdf'.format(year, name).replace('/', ' ')
        if url.endswith('pdf'):
            crawler.download(url, filename)
        else:
            crawler.open_new_tab()
            crawler.get(url)
            try:
                file_url = crawler.get_attr('#textContainer1 a', 'href')
            except Exception:
                pass
            crawler.download(file_url, filename)
            crawler.close_current_tab()
        crawler.upload_to_ftp(filename)
    crawler.close()
