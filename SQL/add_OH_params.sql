INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_OH.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_OH.sh', 'ohio');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('ohio', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('ohio', 'fs_server', '', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('ohio', 'fs_username', '', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('ohio', 'fs_password', '', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('ohio', 'fs_share', '', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('ohio', 'fs_directory_prefix', '', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- connecticut
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('ohio', 'url', 'http://ohioauditor.gov/auditsearch/Search.aspx', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('ohio', 'downloads_path', '/tmp/downloads/OH/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('ohio', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
