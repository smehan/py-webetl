create table match_cw (
    pk_id int not null AUTO_INCREMENT,
    az_pk_id int,
    wal_pk_id int,
    net decimal(8,2),
    roi decimal(8,2),
    match_score decimal(5,2),
    match_meth varchar(4),
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (pk_id)
)

-- Unable to set a foreign key on product_pk_id since at time of insert don't have both, so why
-- favor one when there could be multiple other products...