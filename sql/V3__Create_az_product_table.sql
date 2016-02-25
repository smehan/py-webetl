create table az_product (
    pk_id int not null AUTO_INCREMENT,
    title varchar(150) not null,
    asin varchar(12) not null,
    price decimal(8,2) not null,
    weight float,
    shipping_cost decimal(8,2),
    sales_rank int,
    avg_rate float,
    num_reviews int,
    url varchar(100),
    img varchar(100),
    upc varchar(20),
    last_read TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_changed TIMESTAMP DEFAULT '0000-00-00 00:00:00',
    PRIMARY KEY (pk_id)
)