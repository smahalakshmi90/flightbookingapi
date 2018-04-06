INSERT INTO "TemplateFlight" VALUES(1234,"20:52","23:40",'Finland','France');
INSERT INTO "TemplateFlight" VALUES(1235,"10:50","13:10",'Finland','Spain');
INSERT INTO "TemplateFlight" VALUES(1236,"07:30","09:10",'Finland','Sweeden');
INSERT INTO "TemplateFlight" VALUES(1237,"04:00","06:00",'Finland','Berlin');
INSERT INTO "TemplateFlight" VALUES(1238,"20:52","23:40",'Finland','Poland');


INSERT INTO "Flight" VALUES(1111,'AY101',200,'GATE02',"2018-05-06","2018-05-07",90,10,1234);
INSERT INTO "Flight" VALUES(1122,'AY201',150,'GATE04',"2018-06-10","2018-06-10",90,15,1235);
INSERT INTO "Flight" VALUES(1133,'AY523',180,'GATE01',"2018-07-05","2018-07-05",90,0,1237);


INSERT INTO "User" VALUES(1,'Tilton','John', "92722736387",'john.tilton@jhj.jh',"1981-04-04",'male',1519423463929);
INSERT INTO "User" VALUES(2,'Sam','Jacob', "927656756",'sam.jacob@jhj.jh',"1981-04-05",'male',1519423463929);
INSERT INTO "User" VALUES(3,'Simon','Johni', "895454587",'simon.johni@jhj.jh',"1989-04-07",'male',1519423463929);
INSERT INTO "User" VALUES(4,'Mike','Jac',"89766736387",'mic.jac@jhj.jh',"1985-09-01",'male',1519423463929);
INSERT INTO "User" VALUES(5,'Niil','Jain', "454555667",'niil.jain@jhj.jh',"1983-03-04",'male',1519423463929);

INSERT INTO "Reservation" VALUES(11,'AB12CS',"2018-02-20",1,1111);
INSERT INTO "Reservation" VALUES(22,'HJJJHW',"2018-02-28",2,1122);
INSERT INTO "Reservation" VALUES(33,'ABGJHG',"2018-02-09",3,1133);
INSERT INTO "Reservation" VALUES(44,'OIOYHA',"2018-08-30",5,1133);


INSERT INTO "Ticket" VALUES(1010,'John','Tilton','male',20,11,'21A');
INSERT INTO "Ticket" VALUES(1020,'Jacob','Tilton','male',25,11,'21B');
INSERT INTO "Ticket" VALUES(1030,'Sam','Jacob','male',29,22,'1A');
INSERT INTO "Ticket" VALUES(1040,'Molly','Jacob','female',40,22,'1B');
INSERT INTO "Ticket" VALUES(1050,'Niil','Jain','male',29,44,'15A');

