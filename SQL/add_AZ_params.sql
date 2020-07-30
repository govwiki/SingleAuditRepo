INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_AZ.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_AZ.sh', 'arizona');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'fs_server', '', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'fs_username', '', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'fs_password', '', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'fs_share', '', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'fs_directory_prefix', '', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- connecticut
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'url', 'http://portal.sao.wa.gov/ReportSearch', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'downloads_path', '/tmp/downloads/AZ/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('arizona', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
