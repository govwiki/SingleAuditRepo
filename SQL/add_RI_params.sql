INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_RI.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_RI.sh', 'rhode island');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'fs_server', '', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'fs_username', '', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'fs_password', '', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'fs_share', '', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'fs_directory_prefix', '', 'File Storage base folder for uploads (leave blank to upload to general storage)');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'dir_pdfs', '', '');
