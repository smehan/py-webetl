create table census_tract_2010 (
    pk_id int not null AUTO_INCREMENT,
    track_id bigint not null,
    track_name varchar(25),
    PRIMARY KEY (pk_id)
);