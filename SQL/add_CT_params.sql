INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_CT.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_CT.sh', 'connecticut');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'fs_server', '', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'fs_username', '', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'fs_password', '', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'fs_share', '', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'fs_directory_prefix', '', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- connecticut
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'url', 'https://www.appsvcs.opm.ct.gov/Auditing/Public/Report.aspx', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'downloads_path', '/tmp/downloads/CT/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'upload_date', '8/1/2019', 'Documents uploaded after this date');
