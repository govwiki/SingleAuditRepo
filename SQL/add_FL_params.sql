INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_FL.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_FL.sh', 'florida,general');

-- general
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('florida', 'headless_mode', 'True', 'for invisible (True) or visible (False) firefox');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('florida', 'fs_server', 'https://cafr.file.core.windows.net', 'File Storage URL');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('florida', 'fs_username', 'cafr', 'File Storage username');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('florida', 'fs_password', 'OsA9Q0AHx1dNG2CZEyRxRyUL3XL7DMpChsNBYW8yzmSJOXIZNL2gDtELb/q72PZ4wODl5WITaCxqL6iI+tv0pw==', 'File Storage password');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('florida', 'fs_share', 'cafr', 'File Storage share name');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('florida', 'fs_directory_prefix', '', 'File Storage base folder for uploads (leave blank to upload to general storage)');

-- florida
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('florida', 'urls', 'https://flauditor.gov/pages/municipalities_efiles.html
https://flauditor.gov/pages/counties_efiles.html
https://flauditor.gov/pages/special%20districts_efiles.html
https://flauditor.gov/pages/dsb_efiles.html', 'target urls');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('florida', 'downloads_path', '/tmp/downloads/FL/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('florida', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');