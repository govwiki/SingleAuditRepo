CREATE TABLE `govwiki_production`.`script_file_status` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `script_name` VARCHAR(1000) NOT NULL,
  `file_original_name` VARCHAR(1000) NULL,
  `file_upload_path` VARCHAR(2000) NULL,
  `file_upload_name` VARCHAR(1000) NULL,
  `file_status` ENUM('None', 'Downloaded', 'Classified', 'Uploaded', 'Other') NOT NULL,
  PRIMARY KEY (`id`));