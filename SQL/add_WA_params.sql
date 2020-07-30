INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_WA.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_SA.sh', 'washington');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'fs_server', '', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'fs_username', '', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'fs_password', '', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'fs_share', '', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'fs_directory_prefix', '', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- connecticut
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'url',  'http://portal.sao.wa.gov/ReportSearch', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'downloads_path', '/tmp/downloads/WA/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('washington', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
