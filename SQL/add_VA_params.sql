INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_VA.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_VA.sh', 'virginia');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('virginia', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('virginia', 'fs_server', '', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('virginia', 'fs_username', '', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('virginia', 'fs_password', '', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('virginia', 'fs_share', '', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('virginia', 'fs_directory_prefix', '', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- connecticut
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('virginia', 'url', 'http://www.apa.virginia.gov/APA_Reports/localgov_cafrs.aspx', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('virginia', 'downloads_path', '/tmp/downloads/VA/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('virginia', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('virginia', 'year', '2018', 'Fiscal Year');
