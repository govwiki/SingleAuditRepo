ALTER TABLE `govwiki_production`.`script_file_status` 
ADD COLUMN `notes` VARCHAR(2000) NULL AFTER `file_status`;
