INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_GA.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_GA.sh', 'georgia');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'fs_server', '', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'fs_username', '', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'fs_password', '', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'fs_share', '', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'fs_directory_prefix', '', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- connecticut
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'url', 'https://ted.cviog.uga.edu/financial-documents/financial-reports', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'downloads_path', '/tmp/downloads/GA/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('georgia', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
