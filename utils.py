import glob
import os
import sys
import time
import urllib.request
from ftplib import FTP
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.support.ui import Select


class Crawler:
    def __init__(self, config, section):
        self.downloads_path = config.get(section, 'downloads_path', fallback='/tmp/downloads/')
        if not os.path.exists(self.downloads_path):
            os.makedirs(self.downloads_path)
        elif not os.path.isdir(self.downloads_path):
            print('ERROR:{} downloads_path parameter points to file!'.format(section))
            sys.exit(1)
        if config.getboolean('general', 'headless_mode', fallback=False):
            display = Display(visible=0, size=(1920, 1080))
            display.start()
        self.config = config
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        prefs = {
            'download.default_directory': self.downloads_path,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True,
        }
        options.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(chrome_options=options, service_args=["--verbose", "--log-path=/tmp/selenium.log"])
        self.browser.implicitly_wait(10)

    def get(self, url):
        self.browser.get(url)
        time.sleep(3)

    def wait_for_displayed(self, selector):
        element = self.browser.find_element_by_css_selector(selector)
        while not element.is_displayed():
            pass

    def click_by_text(self, text):
        self.browser.find_element_by_link_text(text)
        time.sleep(3)

    def click_xpath(self, path, single=True):
        if single:
            self.browser.find_element_by_xpath(path).click()
        else:
            for el in self.browser.find_elements_by_xpath(path):
                el.click()
        time.sleep(3)

    def click(self, selector, single=True):
        if single:
            self.browser.find_element_by_css_selector(selector).click()
        else:
            for el in self.browser.find_elements_by_css_selector(selector):
                el.click()
        time.sleep(3)

    def send_keys(self, selector, keys):
        elem = self.browser.find_element_by_css_selector(selector)
        elem.clear()
        elem.send_keys(keys)
        time.sleep(3)

    def get_text(self, selector):
        return self.browser.find_element_by_css_selector(selector).text

    def get_attr(self, selector, attr, single=True):
        if single:
            return self.browser.find_element_by_css_selector(selector).get_attribute(attr)
        return [el.get_attribute(attr) for el in self.browser.find_elements_by_css_selector(selector)]

    def execute(self, script):
        self.browser.execute_script(script, [])
        time.sleep(3)

    def deselect_all(self, selector):
        select = Select(self.browser.find_element_by_css_selector(selector))
        select.deselect_all()
        time.sleep(3)

    def select_option(self, selector, option):
        select = Select(self.browser.find_element_by_css_selector(selector))
        select.select_by_visible_text(option)
        time.sleep(3)

    def select_option_by_index(self, selector, index):
        select = Select(self.browser.find_element_by_css_selector(selector))
        if index < len(select.options):
            select.select_by_index(index)
            time.sleep(3)
            return True
        return False

    def close(self):
        self.browser.quit()

    def download(self, url, filename):
        print('Downloading', url)
        try:
            r = urllib.request.urlopen(url)
            with open(os.path.join(self.downloads_path, filename), 'wb') as f:
                f.write(r.read())
        except Exception:
            print('ERROR: Downloading failed!')

    def _get_remote_filename(local_filename):
        raise NotImplemented

    def upload_to_ftp(self):
        return
        pdf_paths = glob.glob(self.downloads_path + "*.pdf")
        pdf_paths.sort()

        try:
            ftp = FTP()
            ftp.connect(
                self.config.get('general', 'ftp_server').strip(),
                int(self.config.get('general', 'ftp_port')),
            )
            ftp.login(
                user=self.config.get('general', 'ftp_username').strip(),
                passwd=self.config.get('general', 'ftp_password').strip(),
            )
            # ftp.prot_p() if using FTP_TLS uncomment this line
            print("Connection to ftp successfully established...")

            for path in pdf_paths:
                pdf_filename = os.path.basename(path)
                pdf_file = open(path, 'rb')
                remote_filename = self._get_remote_filename(pdf_filename)
                if not remote_filename:
                    continue
                directory, filename = remote_filename
                if not self.config.getboolean('virginia', 'overwrite_remote_files', fallback=False):
                    if filename in [f[0] for f in ftp.mlsd(directory)]:
                        continue
                ftp.cwd('/{}'.format(directory))
                ftp.storbinary('STOR {}'.format(filename), pdf_file)
                pdf_file.close()
                break
            ftp.quit()
        except Exception as e:
            print(str(e))
