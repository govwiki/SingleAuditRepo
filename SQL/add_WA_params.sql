INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_WA.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_SA.sh', 'washington');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'fs_server', 'https://cafr.file.core.windows.net', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'fs_username', 'cafr', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'fs_password', 'OsA9Q0AHx1dNG2CZEyRxRyUL3XL7DMpChsNBYW8yzmSJOXIZNL2gDtELb/q72PZ4wODl5WITaCxqL6iI+tv0pw==', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'fs_share', 'cafr', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'fs_directory_prefix', 'Unclassified/test_wa', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- connecticut
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'url',  'http://portal.sao.wa.gov/ReportSearch', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'downloads_path', '/tmp/downloads/WA/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');