INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_NC.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_NC.sh', 'north_carolina');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('north_carolina', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('north_carolina', 'fs_server', '', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('north_carolina', 'fs_username', '', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('north_carolina', 'fs_password', '', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('north_carolina', 'fs_share', '', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('north_carolina', 'fs_directory_prefix', '', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- connecticut
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('north_carolina', 'url', 'https://www.auditor.nc.gov/pub42/ReportsList.aspx?DocType=1&AuditID=2', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('north_carolina', 'downloads_path', '/tmp/downloads/NC/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('north_carolina', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
