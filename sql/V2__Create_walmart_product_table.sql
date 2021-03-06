create table walmart_product (
    pk_id int not null AUTO_INCREMENT,
    title varchar(150) not null,
    url varchar(200) not null,
    price decimal(8,2) not null,
    img varchar(200),
    item_id varchar(10),
    upc varchar(20),
    last_read TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_changed TIMESTAMP DEFAULT '0000-00-00 00:00:00',
    PRIMARY KEY (pk_id)
)