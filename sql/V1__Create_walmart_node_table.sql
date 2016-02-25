-- initialize and populate the walmart_node table with the toy categories.
-- timestamps are set in the past to allow for immediate use
create table walmart_node (
    pk_id int not null AUTO_INCREMENT,
    node varchar(100) not null,
    last_read timestamp,
    PRIMARY KEY (pk_id)
);

insert into walmart_node (node, last_read)
    values ('/toys/action-figures/4171_4172', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/action-figures/4171_4172_1156794', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/action-figures/4171_4172_1231181', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/action-figures/4171_4172_1224720', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/action-figures/4171_4172_1224721', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/action-figures/4171_4172_1230589',date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/action-figures/4171_4172_1156793', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/action-figures/4171_4172_1228672', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/ride-on-toys/4171_133073_5353', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/scooters/4171_133073_132589', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/kids-bikes/4171_133073_1085618', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/pedal-push/4171_133073_5354', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/wagons/4171_133073_91644', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/wagons/4171_133073_91644', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/adult-bikes/4171_133073_1085617', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/tricycles/4171_133073_1229904', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/skateboards/4171_133073_5250', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/rockers/4171_133073_626379', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/roller-skates/4171_133073_658124', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/building-sets/4171_4186_1044000', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/bricks-blocks/4171_4186_133013', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/dollhouses-play-sets/4171_4187_133126', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/fashion-dolls/4171_4187_133047', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/baby-dolls/4171_4187_133124', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/doll-clothes-accessories/4171_4187_1074304', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/stuffed-animals-plush/4171_4187_132874', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/collectible-dolls/4171_4187_132911', date_sub(now(), INTERVAL 30 day));
insert into walmart_node (node, last_read)
    values ('/toys/robots-electronic-pets/4171_4187_1105996', date_sub(now(), INTERVAL 30 day));
