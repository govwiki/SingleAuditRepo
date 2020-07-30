INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_OR.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_OR.sh', 'oregon');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'fs_server', '', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'fs_username', '', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'fs_password', '', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'fs_share', '', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'fs_directory_prefix', '', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- illinois
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'url', 'https://secure.sos.state.or.us/muni/public.do', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('oregon', 'downloads_path', '/tmp/downloads/OR/', 'temp (local) folder for file downloads');
