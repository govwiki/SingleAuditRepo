import os
import ssl
import sys
import time
import urllib.request
#import urllib.parse
from azure.storage.file import FileService, ContentSettings
from ftplib import FTP, error_perm
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from fileinput import filename
from email._header_value_parser import Section
import mysql.connector
import re

class Crawler:

    def __init__(self, config, section, script_name = None, error_message = None):
        self.script_name = script_name
        self.config = config
        self.db = DbCommunicator(config)
        self.error_message = error_message
        try:
            self.section = section
            self.dbparams = self.db.readProps('general')
            self.dbparams.update(self.db.readProps(section))
            self.downloads_path = self.get_property('downloads_path', section)
            self.overwrite_remote_files = self.get_property('overwrite_remote_files', section, 'bool')
            if not os.path.exists(self.downloads_path):
                os.makedirs(self.downloads_path)
            elif not os.path.isdir(self.downloads_path):
                print('ERROR:{} downloads_path parameter points to file!'.format(section))
                sys.exit(1)
            self.headless_mode = self.get_property('headless_mode', 'general', 'bool')
            if self.headless_mode:
                display = Display(visible=0, size=(1920, 1080))
                display.start()
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
        
            # self.ftp_connect()
            self.file_storage_connect()
        except Exception as e:
            self.error_message = str(e)
        
    def get_property(self, prop, section, type='str'):
        if type=='str':
            if self.dbparams is not None and prop in self.dbparams:
                return self.dbparams[prop]
            else:
                return self.config.get(section, prop).strip()
        elif type=='bool':
            if self.dbparams is not None and prop in self.dbparams:
                return self.dbparams[prop]=='True'
            else:
                return self.config.getboolean(section, prop, fallback=False)
        
    def file_storage_connect(self):
        self.file_storage_url = self.get_property('fs_server', 'general')
        self.file_storage_user = self.get_property('fs_username', 'general')
        self.file_storage_pwd = self.get_property('fs_password', 'general')
        self.file_storage_share = self.get_property('fs_share', 'general')
        self.file_storage_dir = self.get_property('fs_directory_prefix', 'general')
        self.file_service = FileService(account_name=self.file_storage_user, account_key=self.file_storage_pwd) 
        try:
            if self.file_service.exists(self.file_storage_share):
                print('Connection to Azure file storage successfully established...')
                if len(self.file_storage_dir) > 0 and not self.file_service.exists(self.file_storage_share, directory_name=self.file_storage_dir):
                    subdirs = self.file_storage_dir.split('/')
                    subdirfull=""
                    for subdir in subdirs:
                        subdirfull+=subdir
                        self.file_service.create_directory(self.file_storage_share, subdirfull)
                        subdirfull+="/"
                    print('Created directory:' + self.file_storage_dir)
            else:
                print('Filaed to connect to Asure file storage, share does not exist: ' + self.file_storage_share)
        except Exception as ex:
            print('Error connecting to Azure file storage: ', ex)
        
    def ftp_connect(self):
        self.ftp = FTP()
        self.ftp.connect(
            self.config.get('general', 'ftp_server').strip(),
            int(self.config.get('general', 'ftp_port')),
        )
        self.ftp.login(
            user=self.config.get('general', 'ftp_username').strip(),
            passwd=self.config.get('general', 'ftp_password').strip(),
        )
        print('Connection to ftp successfully established...')

    def get(self, url):
        self.browser.get(url)
        time.sleep(3)

    def assert_exists(self, selector):
        _ = self.browser.find_element_by_css_selector(selector)

    def get_elements(self, selector, root=None):
        if root is None:
            root = self.browser
        return root.find_elements_by_css_selector(selector)

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

    def click(self, selector, single=True, root=None):
        if root is None:
            root = self.browser
        if single:
            root.find_element_by_css_selector(selector).click()
        else:
            for el in root.find_elements_by_css_selector(selector):
                el.click()
        time.sleep(3)

    def send_keys(self, selector, keys):
        elem = self.browser.find_element_by_css_selector(selector)
        elem.clear()
        elem.send_keys(keys)
        time.sleep(3)

    def open_new_tab(self):
        self.browser.execute_script("window.open('');")
        self.browser.switch_to.window(self.browser.window_handles[1])

    def close_current_tab(self):
        self.browser.close()
        self.browser.switch_to.window(self.browser.window_handles[-1])

    def get_text(self, selector, single=True, root=None):
        if root is None:
            root = self.browser
        if single:
            return root.find_element_by_css_selector(selector).text
        return [el.text for el in root.find_elements_by_css_selector(selector)]

    def get_attr(self, selector, attr, single=True, root=None):
        if root is None:
            root = self.browser
        if single:
            return root.find_element_by_css_selector(selector).get_attribute(attr)
        return [el.get_attribute(attr) for el in root.find_elements_by_css_selector(selector)]

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

    def back(self):
        self.browser.back()
        time.sleep(3)

    def close(self):
        if hasattr(self,'browser'):
            self.browser.quit()
        if hasattr(self,'db'):
            self.db.close()
        # self.ftp.quit()

    def download(self, url, filename, file_db_id=None):
        # print('Downloading', filename, self._get_remote_filename(filename))
        # return
        if url.startswith('https'):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        else:
            ctx = None
        
        content_length = 1
        retry = 0
        file_size = 0
        file_name = ''
        while file_size != content_length and retry < 3:
            try:
                r = urllib.request.urlopen(url, context=ctx)
                content_length = r.length
                file_name = os.path.join(self.downloads_path, filename)
                with open(file_name, 'wb') as f:
                    f.write(r.read())
                    file_size = os.stat(file_name).st_size
                    retry += 1
                    # print('Attempt', retry, 'Downloaded', file_size, 'bytes of', content_length)
            except Exception as e:
                retry += 1
                print('Attempt', retry, 'ERROR: Downloading failed!', url, str(e))
                try:  
                    os.remove(file_name)
                except OSError:
                    pass
        if file_size == content_length:
            if file_db_id:
                self.db.saveFileStatus(id = file_db_id, script_name = self.script_name, file_original_name = filename, file_status = 'Downloaded')
            else:
                self.db.saveFileStatus(script_name = self.script_name, file_original_name = filename, file_status = 'Downloaded')
        else:
            if file_db_id:
                self.db.saveFileStatus(id = file_db_id, script_name = self.script_name, file_original_name = filename, file_status = 'None')
            else:
                self.db.saveFileStatus(script_name = self.script_name, file_original_name = filename, file_status = 'None')

    def _get_remote_filename(self, local_filename):
        raise NotImplemented

    def merge_files(self, filenames):
        pdfline = ' '.join(filenames)
        res_filename = filenames[0].split(' part')[0] + '.pdf'
        command = 'pdftk ' + pdfline + ' cat output ' + res_filename
        os.system(command)
        return res_filename

    def upload_to_ftp(self, filename):
        self.upload_to_file_storage(filename)

    def upload_to_ftp_old(self, filename):
        retries = 0
        while retries < 3:
            try:
                path = os.path.join(self.downloads_path, filename)
                # print('Uploading {}'.format(path))
                pdf_file = open(path, 'rb')
                remote_filename = self._get_remote_filename(filename)
                if not remote_filename:
                    return
                directory, filename = remote_filename
                try:
                    self.ftp.cwd('/{}'.format(directory))
                except Exception:
                    self.ftp.mkd('/{}'.format(directory))
                    self.ftp.cwd('/{}'.format(directory))
                if not self.overwrite_remote_files:
                    # print('Checking if {}/{} already exists'.format(directory, filename))
                    try:
                        self.ftp.retrbinary('RETR {}'.format(filename), lambda x: x)
                        return
                    except error_perm:
                        pass
    
                self.ftp.storbinary('STOR {}'.format(filename), pdf_file)
                # print('{} uploaded'.format(path))
                pdf_file.close()
                retries = 3
            except Exception as e:
                print('Error uploading to ftp,', str(e))
                retries += 1
                try:
                    self.ftp.voidcmd("NOOP")
                except Exception as ex:
                    self.ftp_connect()

    def move_to_another(self, filename):
        try:
            entity_type = filename.split('|')[1]
            remote_filename = self._get_remote_filename(filename)
            if not remote_filename:
                return
            if (entity_type == 'County') or (entity_type == 'City') or \
                    (entity_type == 'Township') or (entity_type == 'Village'):
                return
            directory, server_filename = remote_filename
            self.ftp.rename('/General Purpose/{}'.format(server_filename), '/{}/{}'.format(directory, server_filename))
            print('Moved {} to {}'.format(server_filename, directory))
        except Exception as e:
            print(str(e))
            
    def upload_to_file_storage(self, filename):
        fnm = FilenameManager()
        retries = 0
        while retries < 3:
            try:
                path = os.path.join(self.downloads_path, filename)
                file_details = self.db.readFileStatus(file_original_name=filename, file_status = 'Uploaded')
                if file_details is not None:
                    print('File {} was already uploaded before'.format(filename))
                    return
                file_details = self.db.readFileStatus(file_original_name=filename, file_status = 'Other', notes = 'Uplodaed Before')
                if file_details is not None:
                    print('File {} was already uploaded before'.format(filename))
                    return
                file_details = self.db.readFileStatus(file_original_name=filename, file_status = 'Downloaded')
                print('Uploading {}'.format(path))
                remote_filename = self._get_remote_filename(filename)
                old_filename = filename
                directory = None
                if not remote_filename:
                    return
                try:
                    directory, filename, year = remote_filename
                except:
                    directory, filename = remote_filename
                filename = fnm.azure_validate_filename(filename)
                if len(self.file_storage_dir) > 0:
                    directory = self.file_storage_dir + '/' + directory
                if not self.file_service.exists(self.file_storage_share, directory_name=directory):
                    self.file_service.create_directory(self.file_storage_share, directory)
                if year:
                    directory += '/' + year
                    if not self.file_service.exists(self.file_storage_share, directory_name=directory):
                        self.file_service.create_directory(self.file_storage_share, directory)
                if not self.overwrite_remote_files:
                    print('Checking if {}/{} already exists'.format(directory, filename))
                    if self.file_service.exists(self.file_storage_share, directory_name=directory, file_name=filename):
                        print('{}/{} already exists'.format(directory, filename))
                        if file_details is None:
                            self.db.saveFileStatus(script_name = self.script_name, file_original_name=old_filename, file_upload_path = directory, file_upload_name = filename, file_status = 'Other', notes = 'Uplodaed Before')
                        else:
                            self.db.saveFileStatus(id = file_details['id'], file_upload_path = directory, file_upload_name = filename, file_status = 'Other', notes = 'Uplodaed Before')
                        return
                self.file_service.create_file_from_path(
                    self.file_storage_share,
                    directory,
                    filename,
                    path,
                    content_settings=ContentSettings(content_type='application/pdf'))
                if file_details is None:
                    self.db.saveFileStatus(script_name = self.script_name, file_original_name=old_filename, file_upload_path = directory, file_upload_name = filename, file_status = 'Uploaded')
                else:
                    self.db.saveFileStatus(id = file_details['id'], file_upload_path = directory, file_upload_name = filename, file_status = 'Uploaded')     
                print('{} uploaded'.format(path))
                retries = 3
            except Exception as e:
                print('Error uploading to Asure file storage,', str(e))
                retries += 1

                
class DbCommunicator:

    def __init__(self, config):
        self.db_url = config.get('sql', 'url', fallback='127.0.0.1')
        self.db_user = config.get('sql', 'user', fallback='govwiki')
        self.db_password = config.get('sql', 'password', fallback='test123')
        self.db_name = config.get('sql', 'name', fallback='govwiki_production')
        self.connect()
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(user=self.db_user, password=self.db_password,
                              host=self.db_url,
                              database=self.db_name) 
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Failed to connect to database: wrong credentials")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Failed to connect to database: Database does not exist ", self.db_name)
            else:
                print("Failed to connect to database:", err)
        
    def log(self, name, start, end, config, result, error):
        statement = None
        try:
            statement = self.connection.cursor()
        except (mysql.connector.InterfaceError, mysql.connector.errors.OperationalError) as e:
            print("Error accessing database, trying to reconnect")
            self.connect()
            statement = self.connection.cursor()
        try:
            query = ("INSERT INTO script_execution_log "
                   "(name, start_time, end_time, config_file, result, error_message) "
                   "VALUES (%s, %s, %s, %s, %s, %s)")
            data = (name, start, end, config, result, error)
            statement.execute(query, data)
            self.connection.commit()
        except mysql.connector.InterfaceError as e:
            print("Error wringing log to database:", e)
        finally:
            if statement:
                statement.close()
            
    def readProps(self, category):
        props = {}
        statement = None
        try:
            statement = self.connection.cursor()
        except mysql.connector.InterfaceError as e:
            print("Error accessing database, trying to reconnect")
            self.connect()
            statement = self.connection.cursor()
        try:
            query = ("SELECT `key`, value FROM script_parameters "
                   "WHERE category = %s")
            data = (category,)
            statement.execute(query, data)
            for (key,value) in statement:
                props[key]=value
        except Exception as e:
            print("Error reading from database:", e)
        finally:
            if statement:
                statement.close()
        return props
        
    def saveFileStatus(self, **kwargs):
        result = None
        if kwargs is not None:
            statement = None
            try:
                statement = self.connection.cursor()
            except Exception as e:
                print("Error accessing database, trying to reconnect")
                self.connect()
                statement = self.connection.cursor()
            query = None
            data = None 
            if "id" in kwargs:
                query = "UPDATE script_file_status SET "
                i = 0
                for key in kwargs:
                    if key == "id":
                        pass
                    elif i == 0:
                        query += key+" = %s"
                        data = (kwargs[key],)
                        i+=1
                    else:
                          query += ", " + key + " = %s"
                          data += (kwargs[key],)
                          i+=1
                if i > 0:
                    query += " WHERE id = %s"
                    data += (kwargs["id"],)
                else:
                    query = None
                    data = None
            else:
                query = "INSERT INTO script_file_status ("
                data = None
                query_values = "("
                i = 0
                for key in kwargs:
                    if i == 0:
                        query += key
                        query_values +="%s"
                        data = (kwargs[key],)
                        i+=1
                    else:
                        query += ", "+key
                        query_values +=",%s"
                        data += (kwargs[key],)
                        i+=1
                if i>0:
                    query += ") VALUES " + query_values + ")"
                else:
                    query = None
                    data = None
            if query is not None:
                try:
                    statement.execute(query, data)
                    if "id" in kwargs:
                        result = kwargs["id"]
                    else:
                        result = statement.lastrowid
                    self.connection.commit()
                except Exception as e:
                    print("Error reading from database:", e)
                finally:
                    if statement:
                        statement.close()
        return result
    
    def readFileStatus(self, **kwargs):
        result = None
        if kwargs is not None:
            statement = None
            try:
                statement = self.connection.cursor()
            except mysql.connector.InterfaceError as e:
                print("Error accessing database, trying to reconnect")
                self.connect()
                statement = self.connection.cursor()
            query = "SELECT * FROM script_file_status WHERE "
            data = None
            i = 0
            for key in kwargs:
                if i == 0:
                    query += key +" = %s"
                    data = (kwargs[key],)
                    i+=1
                else:
                    query += " AND "+key+" = %s"
                    data += (kwargs[key],)
                    i+=1
            query +=" LIMIT 1"
            if i == 0:
                query = None
            if query is not None:
                try:
                    statement.execute(query, data)
                    for (id, script_name, file_original_name, file_upload_path, file_upload_name, file_status, notes) in statement:
                        result = {'id': id, 'script_name': script_name, 'file_original_name': file_original_name, 'file_upload_path': file_upload_path, 'file_upload_name': file_upload_name, 'file_status': file_status, 'notes': notes}
                except Exception as e:
                    print("Error reading from database:", e)
                finally:
                    if statement:
                        statement.close()
        return result
    
    def close(self):
        try:
            self.connection.close()
        except:
            pass
        
class FilenameManager:
    
    def __init__(self):
        #Directory and file component names must be no more than 255 characters in length.
        self.azure_max_length = 255
        
        #Directory names cannot end with the forward slash character (/). If provided, it will be automatically removed.
        #File names must not end with the forward slash character (/).
        self.azure_forbid_in_end = ['/',]
        
        #Reserved URL characters must be properly escaped.
        self.azure_escape = [';', '/', '?', ':', '@', '=', '&',]
        
        #The following characters are not allowed: " \ / : | < > * ?        
        self.azure_forbid_symbol = ['"', '\\', ':', '|', '<', '>', '*', '?', '\a', '\b', '\cx', '\e', '\f', '\M-\C-x', '\n', '\r', '\t', '\v',]
        
        #The following file names are not allowed: LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9, COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9, PRN, AUX, NUL, CON, CLOCK$, dot character (.), and two dot characters (..).
        self.azure_forbid_filename = ['LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'PRN', 'AUX', 'NUL', 'CON', 'CLOCK$', '.', '..',]        

    def azure_check_length(self, name):
        new_name = name
        if len(name)>self.azure_max_length:
            start = name[:self.max_length-9]
            end = name[-8:]
            new_name = start+" "+end
        return new_name
    
    def azure_check_unicode(self, name):
        #Illegal URL path characters not allowed. Code points like \uE000, while valid in NTFS filenames, are not valid Unicode characters. In addition, some ASCII or Unicode characters, like control characters (0x00 to 0x1F, \u0081, etc.), are also not allowed. For rules governing Unicode strings in HTTP/1.1 see RFC 2616, Section 2.2: Basic Rules and RFC 3987.
        new_name = re.sub("U\+00\d(\d|[A-F])","", name)
        return new_name
    
    def azure_check_forbidden_symbols(self,name):
        new_name = self.azure_check_unicode(name)
        for item in self.azure_forbid_symbol:
            new_name = new_name.replace(item,"_")
        return new_name

    def azure_check_forbidden_names(self,name):
        new_name = name
        if name in self.azure_forbid_filename:
            new_name = name+'_1.pdf'
        return new_name
            
    def azure_check_ending(self, name):
        new_name = name
        if name[-1:] in self.azure_forbid_in_end:
            new_name = name[:-1]
        return new_name
    
    def azure_escape_reserved_symbols(self,name):
        #new_name = urllib.parse.quote(name)
        # it turns out Azure doesn't transform escaped sequences back to symbols, thus we just remove them
        new_name = name
        for item in self.azure_escape:
            new_name = new_name.replace(item,"_")
        return new_name
    
    def azure_validate_filename(self,name):
        new_name = self.azure_check_forbidden_symbols(name)
        new_name = self.azure_check_ending(new_name)
        new_name = self.azure_escape_reserved_symbols(new_name)
        new_name = self.azure_check_length(new_name)
        new_name = self.azure_check_forbidden_names(new_name)
        return new_name