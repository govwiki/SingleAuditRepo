import configparser
import urllib.parse
from utils import Crawler


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'arizona')
    for state_url in config.get('arizona', 'urls').split('\n'):
        crawler.get(state_url.strip())
        while True:
            for row in crawler.get_elements('div.views-row'):
                row_type = crawler.get_text('.views-field-field-audit-type', root=row)
                if 'financial audit' in row_type.lower() or 'single audit' in row_type.lower():
                    url = crawler.get_attr('strong a', 'href', root=row)
                    crawler.download(url, urllib.parse.unquote(url).split('/')[-1])
            try:
                crawler.click('.next a')
            except Exception:
                break
