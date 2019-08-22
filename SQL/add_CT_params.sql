INSERT INTO script_mapping (name,executable,param_categories) VALUES ('get_CT.py', 'TZ="America/Los_Angeles" /home/sibers/python_scripts/SingleAuditRepo/get_CT.sh', 'connecticut,general');

-- connecticut
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'url', 'https://www.appsvcs.opm.ct.gov/Auditing/Public/Report.aspx', 'target url');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'downloads_path', '/tmp/downloads/CT/', 'temp (local) folder for file downloads');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'overwrite_remote_files', 'False', 'Overwrite remote files if they already exist');
INSERT INTO script_parameters (category, `key`, value, description) VALUES ('connecticut', 'upload_date', '8/1/2019', 'Documents uploaded after this date');