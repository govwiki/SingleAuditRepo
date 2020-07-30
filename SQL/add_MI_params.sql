INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_MI.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_MI.sh', 'michigan');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('michigan', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('michigan', 'fs_server', '', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('michigan', 'fs_username', '', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('michigan', 'fs_password', '', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('michigan', 'fs_share', '', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('michigan', 'fs_directory_prefix', '', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- michigan
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('michigan', 'url', 'https://treas-secure.state.mi.us/lafdocsearch/TL41W76.aspx', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('michigan', 'downloads_path', '/tmp/downloads/MI/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('michigan', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('michigan', 'year', '2019', 'Fiscal year');
