create table census_tract_2010 (
    pk_id int not null AUTO_INCREMENT,
    track_id int not null,
    track_name varchar(25),
    zip_id int,
    PRIMARY KEY (pk_id),
    FOREIGN KEY (zip_id) REFERENCES zip(pk_id)
);