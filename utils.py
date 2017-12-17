import time
from pyvirtualdisplay import Display
from selenium import webdriver


class Crawler:
    def __init__(self, config):
        self.downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
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
        self.browser.find_element_by_css_selector(selector).send_keys(keys)
        time.sleep(3)

    def get_attr(self, selector, attr, single=True):
        if single:
            return self.browser.find_element_by_css_selector(selector).get_attribute(attr)
        return [el.get_attribute(attr) for el in self.browser.find_elements_by_css_selector(selector)]

    def close(self):
        self.browser.quit()
