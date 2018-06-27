CREATE TABLE `govwiki_production`.`script_parameters` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `category` VARCHAR(200) NOT NULL,
  `key` VARCHAR(200) NOT NULL,
  `value` VARCHAR(2000) NULL,
  `description` LONGTEXT NOT NULL,
  PRIMARY KEY (`id`));


CREATE TABLE `govwiki_production`.`script_mapping` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `executable` VARCHAR(1000) NOT NULL,
  `param_categories` LONGTEXT NOT NULL,
  PRIMARY KEY (`id`));
