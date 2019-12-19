INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_RI.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_RI.sh', 'rhode island');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'fs_server', 'https://cafr.file.core.windows.net', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'fs_username', 'cafr', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'fs_password', 'OsA9Q0AHx1dNG2CZEyRxRyUL3XL7DMpChsNBYW8yzmSJOXIZNL2gDtELb/q72PZ4wODl5WITaCxqL6iI+tv0pw==', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'fs_share', 'cafr', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'fs_directory_prefix', 'Unclassified/test_ri', 'File Storage base folder for uploads (leave blank to upload to general storage)');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('rhode island', 'dir_pdfs', '', '');

