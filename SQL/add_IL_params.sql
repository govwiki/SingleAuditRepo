INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_IL.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_IL.sh', 'illinois');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'fs_server', 'https://cafr.file.core.windows.net', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'fs_username', 'cafr', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'fs_password', 'OsA9Q0AHx1dNG2CZEyRxRyUL3XL7DMpChsNBYW8yzmSJOXIZNL2gDtELb/q72PZ4wODl5WITaCxqL6iI+tv0pw==', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'fs_share', 'cafr', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'fs_directory_prefix', 'Unclassified/test_il', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- illinois
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'url', 'ftp://ftp.illinoiscomptroller.com/LocGovAudits/FY2015/', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'dir_pdfs', '/tmp/downloads/IL/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'dir_in', '/home/sibers/python_scripts/SingleAuditRepo/', 'folder where the script resides');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'year', '2015', 'Fiscal year');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'start_from', '00100000', 'continue download from this item');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'illinois_entities_xlsx_file', 'Illinois Entities.xlsx', 'make sure that file with entities is placed in dir_in directory');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('illinois', 'illinois_entities_sheet', 'Sheet1', 'workbook sheet');