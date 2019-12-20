INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_AZ.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_AZ.sh', 'arizona');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'fs_server', 'https://cafr.file.core.windows.net', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'fs_username', 'cafr', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'fs_password', 'OsA9Q0AHx1dNG2CZEyRxRyUL3XL7DMpChsNBYW8yzmSJOXIZNL2gDtELb/q72PZ4wODl5WITaCxqL6iI+tv0pw==', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'fs_share', 'cafr', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'fs_directory_prefix', 'Unclassified/test_az', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- connecticut
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'url', 'http://portal.sao.wa.gov/ReportSearch', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'downloads_path', '/tmp/downloads/AZ/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'upload_date', '12/20/2019', 'Documents uploaded after this date');
