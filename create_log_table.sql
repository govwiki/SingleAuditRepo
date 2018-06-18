CREATE TABLE `govwiki_production`.`script_execution_log` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `start_time` DATETIME NOT NULL,
  `end_time` DATETIME NOT NULL,
  `config_file` LONGTEXT NULL,
  `result` TINYINT NOT NULL DEFAULT 0,
  `error_message` LONGTEXT NULL,
  PRIMARY KEY (`id`))
COMMENT = 'Logs for pdf download script execution.';
