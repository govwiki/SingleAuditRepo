INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_GA.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_GA.sh', 'georgia');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'fs_server', 'https://cafr.file.core.windows.net', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'fs_username', 'cafr', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'fs_password', 'OsA9Q0AHx1dNG2CZEyRxRyUL3XL7DMpChsNBYW8yzmSJOXIZNL2gDtELb/q72PZ4wODl5WITaCxqL6iI+tv0pw==', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'fs_share', 'cafr', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'fs_directory_prefix', 'Unclassified/test_ga', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- connecticut
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'url', 'https://ted.cviog.uga.edu/financial-documents/financial-reports', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'downloads_path', '/tmp/downloads/GA/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'upload_date', '12/20/2019', 'Documents uploaded after this date');
