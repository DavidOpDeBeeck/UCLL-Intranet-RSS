-- -----------------------------------------------------
-- Table ITEM
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS ITEM (
  'guid' TEXT NOT NULL PRIMARY KEY,
  'title' TEXT NOT NULL,
  'description' TEXT NOT NULL,
  'pubDate' INT NOT NULL,
  'author' TEXT NOT NULL
);

-- -----------------------------------------------------
-- Table CATEGORY
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS CATEGORY (
  'url' TEXT NOT NULL PRIMARY KEY,
  'text' TEXT NOT NULL
);

-- -----------------------------------------------------
-- Table ITEM_has_CATEGORY
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS 'ITEM_has_CATEGORY' (
  'item_guid' TEXT NOT NULL,
  'category_url' TEXT NOT NULL,
  PRIMARY KEY ('item_guid', 'category_url'),
  CONSTRAINT 'fk_CATEGORY_has_ITEM1'
  FOREIGN KEY ('item_guid')
  REFERENCES 'ITEM' ('guid')
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
  CONSTRAINT 'fk_CATEGORY_has_ITEM2'
  FOREIGN KEY ('category_url')
  REFERENCES 'CATEGORY' ('url')
  ON DELETE NO ACTION
  ON UPDATE NO ACTION
);

