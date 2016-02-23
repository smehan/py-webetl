create table zip_tract_cw (
    pk_id int not null AUTO_INCREMENT,
    res_ratio float not null,
    bus_ratio float not null,
    oth_ratio float not null,
    tot_ratio float not null,
    track_pk_id int,
    zip_pk_id int,
    PRIMARY KEY (pk_id),
    FOREIGN KEY (track_pk_id) REFERENCES census_tract_2010(pk_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (zip_pk_id) REFERENCES zip(pk_id) ON DELETE CASCADE ON UPDATE CASCADE
);