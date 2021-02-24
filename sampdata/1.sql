PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE competition (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	input_verifier VARCHAR(4000) NOT NULL, 
	output_verifier VARCHAR(4000) NOT NULL, 
	problem_statement VARCHAR(4000), 
	allow_custom_team_names BOOLEAN, 
	input_upload_begins DATETIME NOT NULL, 
	input_upload_ends DATETIME NOT NULL CHECK (input_upload_ends > input_upload_begins), 
	output_upload_begins DATETIME NOT NULL CHECK (output_upload_begins >= input_upload_ends), 
	output_upload_ends DATETIME NOT NULL CHECK (output_upload_ends > output_upload_begins), 
	verification_begins DATETIME CHECK (verification_begins >= output_upload_ends), 
	verification_ends DATETIME CHECK (verification_ends > verification_begins), 
	resolution_begins DATETIME CHECK (resolution_begins >= verification_ends), 
	resolution_ends DATETIME CHECK (resolution_ends > resolution_begins), 
	open_verification_begins DATETIME CHECK (open_verification_begins >= resolution_ends), 
	open_verification_ends DATETIME CHECK (open_verification_ends >= open_verification_begins), 
	evaluation_begins DATETIME, 
	evaluation_ends DATETIME CHECK (evaluation_ends > evaluation_begins), problem_type VARCHAR(12) DEFAULT 'minimization', 
	PRIMARY KEY (id), 
	CHECK (allow_custom_team_names IN (0, 1))
);
INSERT INTO competition VALUES(1,'Competition 1','{"depot_name": "default", "files": ["default/86461838-ebcf-11e9-9c28-408d5cb80084"], "file_id": "86461838-ebcf-11e9-9c28-408d5cb80084", "path": "default/86461838-ebcf-11e9-9c28-408d5cb80084", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2019-10-11 02:33:35", "_public_url": null}','{"depot_name": "default", "files": ["default/86464858-ebcf-11e9-9c28-408d5cb80084"], "file_id": "86464858-ebcf-11e9-9c28-408d5cb80084", "path": "default/86464858-ebcf-11e9-9c28-408d5cb80084", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2019-10-11 02:33:35", "_public_url": null}',NULL,1,'2019-01-24 20:00:00','2019-01-25 19:59:59','2019-01-25 20:00:00','2019-01-26 19:59:59','2019-01-26 20:00:00','2019-01-27 19:59:59','2019-01-27 20:00:00','2019-01-28 19:59:59','2019-01-28 20:00:00','2019-01-29 19:59:59','2019-01-28 20:00:00','2019-01-29 19:59:59','minimization');
INSERT INTO competition VALUES(2,'Competition 2','{"depot_name": "default", "files": ["default/260ba048-fa33-11e8-8118-6c299560df60"], "file_id": "260ba048-fa33-11e8-8118-6c299560df60", "path": "default/260ba048-fa33-11e8-8118-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:17:02", "_public_url": null}','{"depot_name": "default", "files": ["default/260be01c-fa33-11e8-8118-6c299560df60"], "file_id": "260be01c-fa33-11e8-8118-6c299560df60", "path": "default/260be01c-fa33-11e8-8118-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:17:02", "_public_url": null}','{"depot_name": "default", "files": ["default/260bf750-fa33-11e8-8118-6c299560df60"], "file_id": "260bf750-fa33-11e8-8118-6c299560df60", "path": "default/260bf750-fa33-11e8-8118-6c299560df60", "filename": "ALGOBOWL_F18.pdf", "content_type": "application/pdf", "uploaded_at": "2018-12-07 15:17:02", "_public_url": null}',1,'2019-01-24 20:00:00','2019-01-25 05:59:59','2019-01-25 06:00:00','2019-01-25 19:59:59','2019-01-25 20:00:00','2019-01-26 19:59:59','2019-01-26 20:00:00','2019-01-27 19:59:59','2019-01-27 20:00:00','2019-01-28 19:59:59','2019-01-27 20:00:00','2019-01-28 19:59:59','minimization');
INSERT INTO competition VALUES(3,'Competition 3','{"depot_name": "default", "files": ["default/9f0b6082-fa33-11e8-8118-6c299560df60"], "file_id": "9f0b6082-fa33-11e8-8118-6c299560df60", "path": "default/9f0b6082-fa33-11e8-8118-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:20:25", "_public_url": null}','{"depot_name": "default", "files": ["default/9f0b985e-fa33-11e8-8118-6c299560df60"], "file_id": "9f0b985e-fa33-11e8-8118-6c299560df60", "path": "default/9f0b985e-fa33-11e8-8118-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:20:25", "_public_url": null}','{"depot_name": "default", "files": ["default/9f0bb898-fa33-11e8-8118-6c299560df60"], "file_id": "9f0bb898-fa33-11e8-8118-6c299560df60", "path": "default/9f0bb898-fa33-11e8-8118-6c299560df60", "filename": "ALGOBOWL_F18.pdf", "content_type": "application/pdf", "uploaded_at": "2018-12-07 15:20:25", "_public_url": null}',1,'2019-01-24 20:00:00','2019-01-25 04:59:59','2019-01-25 05:00:00','2019-01-25 05:59:59','2019-01-25 06:00:00','2019-01-25 09:59:59','2019-01-25 10:00:00','2019-01-25 10:59:59','2019-01-25 11:00:00','2019-01-25 11:59:59','2019-01-25 11:00:00','2019-01-25 11:59:59','minimization');
INSERT INTO competition VALUES(4,'Competition 4','{"depot_name": "default", "files": ["default/36b9b938-fa34-11e8-8118-6c299560df60"], "file_id": "36b9b938-fa34-11e8-8118-6c299560df60", "path": "default/36b9b938-fa34-11e8-8118-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:24:39", "_public_url": null}','{"depot_name": "default", "files": ["default/36b9f8d0-fa34-11e8-8118-6c299560df60"], "file_id": "36b9f8d0-fa34-11e8-8118-6c299560df60", "path": "default/36b9f8d0-fa34-11e8-8118-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:24:39", "_public_url": null}','{"depot_name": "default", "files": ["default/36ba0fb4-fa34-11e8-8118-6c299560df60"], "file_id": "36ba0fb4-fa34-11e8-8118-6c299560df60", "path": "default/36ba0fb4-fa34-11e8-8118-6c299560df60", "filename": "ALGOBOWL_F18.pdf", "content_type": "application/pdf", "uploaded_at": "2018-12-07 15:24:39", "_public_url": null}',1,'2019-01-24 20:00:00','2019-01-25 04:59:59','2019-01-25 05:00:00','2019-01-25 05:19:59','2019-01-25 05:20:00','2019-01-25 05:59:59','2019-01-25 06:00:00','2019-01-25 09:59:59','2019-01-25 10:00:00','2019-01-25 10:59:59','2019-01-25 10:00:00','2019-01-25 10:59:59','minimization');
INSERT INTO competition VALUES(5,'Competition 5','{"depot_name": "default", "files": ["default/a14e1974-fa34-11e8-8118-6c299560df60"], "file_id": "a14e1974-fa34-11e8-8118-6c299560df60", "path": "default/a14e1974-fa34-11e8-8118-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:27:38", "_public_url": null}','{"depot_name": "default", "files": ["default/a14e6820-fa34-11e8-8118-6c299560df60"], "file_id": "a14e6820-fa34-11e8-8118-6c299560df60", "path": "default/a14e6820-fa34-11e8-8118-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:27:38", "_public_url": null}','{"depot_name": "default", "files": ["default/a14e911a-fa34-11e8-8118-6c299560df60"], "file_id": "a14e911a-fa34-11e8-8118-6c299560df60", "path": "default/a14e911a-fa34-11e8-8118-6c299560df60", "filename": "ALGOBOWL_F18.pdf", "content_type": "application/pdf", "uploaded_at": "2018-12-07 15:27:38", "_public_url": null}',1,'2019-01-24 20:00:00','2019-01-25 04:59:59','2019-01-25 05:00:00','2019-01-25 05:19:59','2019-01-25 05:20:00','2019-01-25 05:29:59','2019-01-25 05:30:00','2019-01-25 05:59:59','2019-01-25 06:00:00','2019-01-25 19:59:59','2019-01-25 06:00:00','2019-01-25 19:59:59','minimization');
INSERT INTO competition VALUES(6,'ohea','{"depot_name": "default", "files": ["default/169278d8-4aa3-11e9-b72c-6c299560df60"], "file_id": "169278d8-4aa3-11e9-b72c-6c299560df60", "path": "default/169278d8-4aa3-11e9-b72c-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2019-03-19 23:59:53", "_public_url": null}','{"depot_name": "default", "files": ["default/1692cb30-4aa3-11e9-b72c-6c299560df60"], "file_id": "1692cb30-4aa3-11e9-b72c-6c299560df60", "path": "default/1692cb30-4aa3-11e9-b72c-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2019-03-19 23:59:53", "_public_url": null}','{"depot_name": "default", "files": ["default/16931fa4-4aa3-11e9-b72c-6c299560df60"], "file_id": "16931fa4-4aa3-11e9-b72c-6c299560df60", "path": "default/16931fa4-4aa3-11e9-b72c-6c299560df60", "filename": "AlgoBOWL-S19.pdf", "content_type": "application/pdf", "uploaded_at": "2019-03-19 23:59:53", "_public_url": null}',1,'2019-03-03 17:59:11.000000','2019-03-04 17:59:13.000000','2019-03-05 17:59:16.000000','2019-03-06 17:59:18.000000','2019-03-07 17:59:21.000000','2019-03-08 17:59:27.000000','2019-03-09 17:59:29.000000','2019-03-10 17:59:32.000000','2019-03-11 17:59:34.000000','2019-03-12 17:59:36.000000','2019-03-13 17:59:39.000000','2019-03-29 17:59:42.000000','minimization');
INSERT INTO competition VALUES(7,'Unpublished Test','{"depot_name": "default", "files": ["default/84cb7908-e62a-11e9-b08f-6c299560df60"], "file_id": "84cb7908-e62a-11e9-b08f-6c299560df60", "path": "default/84cb7908-e62a-11e9-b08f-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2019-10-03 22:09:50", "_public_url": null}','{"depot_name": "default", "files": ["default/84cbac2a-e62a-11e9-b08f-6c299560df60"], "file_id": "84cbac2a-e62a-11e9-b08f-6c299560df60", "path": "default/84cbac2a-e62a-11e9-b08f-6c299560df60", "filename": "unnamed", "content_type": "application/octet-stream", "uploaded_at": "2019-10-03 22:09:50", "_public_url": null}',NULL,1,'2019-10-31 00:00:00.000000','2020-10-31 00:00:00.000000','2020-10-31 00:00:00.000000','2021-10-31 00:00:00.000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'minimization');
CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	full_name VARCHAR, 
	admin BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email), 
	CHECK (admin IN (0, 1))
);
INSERT INTO user VALUES(28263,'jrosenth','jrosenth@mines.edu','Jack Rosenthal',1);
INSERT INTO user VALUES(28264,'rjosenth','rjosenth@mines.edu','Rack Josenthal',0);
INSERT INTO user VALUES(28265,'mmouse','mmouse@mines.edu','Mickey Mouse',0);
INSERT INTO user VALUES(28266,'minmouse','minmouse@mines.edu','Minnie Mouse',0);
INSERT INTO user VALUES(28267,'dduck','dduck@mines.edu','Donald Duck',0);
INSERT INTO user VALUES(28268,'goofy','goofy@mines.edu','Goofy D. Dawg',0);
CREATE TABLE IF NOT EXISTS "group" (
	id INTEGER NOT NULL, 
	name VARCHAR(100), 
	competition_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(competition_id) REFERENCES competition (id)
);
INSERT INTO "group" VALUES(1,'Team CPW',6);
INSERT INTO "group" VALUES(2,'Mock Turtle',2);
INSERT INTO "group" VALUES(3,'Fast Goat',2);
INSERT INTO "group" VALUES(4,'Steamy Horse',3);
INSERT INTO "group" VALUES(5,'Firey Toad',3);
INSERT INTO "group" VALUES(6,'Twirly Seal',3);
INSERT INTO "group" VALUES(7,'Toasty Donkey',4);
INSERT INTO "group" VALUES(8,'Snappy Alligator',4);
INSERT INTO "group" VALUES(9,'Whippy Penguin',4);
INSERT INTO "group" VALUES(10,'Trippy Snake',5);
INSERT INTO "group" VALUES(11,'Sneaky Lizard',5);
CREATE TABLE user_group_xref (
	user_id INTEGER NOT NULL, 
	group_id INTEGER NOT NULL, 
	PRIMARY KEY (user_id, group_id), 
	FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE ON UPDATE CASCADE, 
	FOREIGN KEY(group_id) REFERENCES "group" (id) ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO user_group_xref VALUES(28263,1);
INSERT INTO user_group_xref VALUES(28264,1);
INSERT INTO user_group_xref VALUES(28265,1);
INSERT INTO user_group_xref VALUES(28263,2);
INSERT INTO user_group_xref VALUES(28264,2);
INSERT INTO user_group_xref VALUES(28265,2);
INSERT INTO user_group_xref VALUES(28263,3);
INSERT INTO user_group_xref VALUES(28267,3);
INSERT INTO user_group_xref VALUES(28268,3);
INSERT INTO user_group_xref VALUES(28263,4);
INSERT INTO user_group_xref VALUES(28265,4);
INSERT INTO user_group_xref VALUES(28266,4);
INSERT INTO user_group_xref VALUES(28263,5);
INSERT INTO user_group_xref VALUES(28264,5);
INSERT INTO user_group_xref VALUES(28267,5);
INSERT INTO user_group_xref VALUES(28263,6);
INSERT INTO user_group_xref VALUES(28265,6);
INSERT INTO user_group_xref VALUES(28268,6);
INSERT INTO user_group_xref VALUES(28263,7);
INSERT INTO user_group_xref VALUES(28264,7);
INSERT INTO user_group_xref VALUES(28266,7);
INSERT INTO user_group_xref VALUES(28267,7);
INSERT INTO user_group_xref VALUES(28263,8);
INSERT INTO user_group_xref VALUES(28264,8);
INSERT INTO user_group_xref VALUES(28268,8);
INSERT INTO user_group_xref VALUES(28264,9);
INSERT INTO user_group_xref VALUES(28265,9);
INSERT INTO user_group_xref VALUES(28266,9);
INSERT INTO user_group_xref VALUES(28263,10);
INSERT INTO user_group_xref VALUES(28264,10);
INSERT INTO user_group_xref VALUES(28268,10);
INSERT INTO user_group_xref VALUES(28263,11);
INSERT INTO user_group_xref VALUES(28265,11);
INSERT INTO user_group_xref VALUES(28266,11);
INSERT INTO user_group_xref VALUES(28267,11);
INSERT INTO user_group_xref VALUES(28263,9);
CREATE TABLE input (
	id INTEGER NOT NULL, 
	data VARCHAR(4000) NOT NULL, 
	group_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_id) REFERENCES "group" (id)
);
INSERT INTO input VALUES(1,'{"depot_name": "default", "files": ["default/2c78b962-fa37-11e8-8118-6c299560df60"], "file_id": "2c78b962-fa37-11e8-8118-6c299560df60", "path": "default/2c78b962-fa37-11e8-8118-6c299560df60", "filename": "input_group2.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:45:51", "_public_url": null}',2);
INSERT INTO input VALUES(2,'{"depot_name": "default", "files": ["default/380cbe72-fa37-11e8-8118-6c299560df60"], "file_id": "380cbe72-fa37-11e8-8118-6c299560df60", "path": "default/380cbe72-fa37-11e8-8118-6c299560df60", "filename": "input_group3.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:46:10", "_public_url": null}',3);
INSERT INTO input VALUES(3,'{"depot_name": "default", "files": ["default/43430ec2-fa37-11e8-8118-6c299560df60"], "file_id": "43430ec2-fa37-11e8-8118-6c299560df60", "path": "default/43430ec2-fa37-11e8-8118-6c299560df60", "filename": "input_group4.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:46:29", "_public_url": null}',4);
INSERT INTO input VALUES(4,'{"depot_name": "default", "files": ["default/4fd114ea-fa37-11e8-8118-6c299560df60"], "file_id": "4fd114ea-fa37-11e8-8118-6c299560df60", "path": "default/4fd114ea-fa37-11e8-8118-6c299560df60", "filename": "input_group5.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:46:50", "_public_url": null}',5);
INSERT INTO input VALUES(5,'{"depot_name": "default", "files": ["default/5af303c4-fa37-11e8-8118-6c299560df60"], "file_id": "5af303c4-fa37-11e8-8118-6c299560df60", "path": "default/5af303c4-fa37-11e8-8118-6c299560df60", "filename": "input_group6.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:47:09", "_public_url": null}',6);
INSERT INTO input VALUES(6,'{"depot_name": "default", "files": ["default/64c27a88-fa37-11e8-8118-6c299560df60"], "file_id": "64c27a88-fa37-11e8-8118-6c299560df60", "path": "default/64c27a88-fa37-11e8-8118-6c299560df60", "filename": "input_group7.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:47:25", "_public_url": null}',7);
INSERT INTO input VALUES(7,'{"depot_name": "default", "files": ["default/7a53de28-fa37-11e8-8118-6c299560df60"], "file_id": "7a53de28-fa37-11e8-8118-6c299560df60", "path": "default/7a53de28-fa37-11e8-8118-6c299560df60", "filename": "input_group8.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:48:01", "_public_url": null}',8);
INSERT INTO input VALUES(8,'{"depot_name": "default", "files": ["default/82e4f0d6-fa37-11e8-8118-6c299560df60"], "file_id": "82e4f0d6-fa37-11e8-8118-6c299560df60", "path": "default/82e4f0d6-fa37-11e8-8118-6c299560df60", "filename": "input_group10.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:48:16", "_public_url": null}',10);
INSERT INTO input VALUES(9,'{"depot_name": "default", "files": ["default/8b73ea9a-fa37-11e8-8118-6c299560df60"], "file_id": "8b73ea9a-fa37-11e8-8118-6c299560df60", "path": "default/8b73ea9a-fa37-11e8-8118-6c299560df60", "filename": "input_group11.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:48:30", "_public_url": null}',11);
INSERT INTO input VALUES(10,'{"depot_name": "default", "files": ["default/d68240e0-fa37-11e8-8118-6c299560df60"], "file_id": "d68240e0-fa37-11e8-8118-6c299560df60", "path": "default/d68240e0-fa37-11e8-8118-6c299560df60", "filename": "input_group9.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 15:50:36", "_public_url": null}',9);
INSERT INTO input VALUES(11,'{"depot_name": "default", "files": ["default/8f2b9962-fa46-11e8-8118-6c299560df60"], "file_id": "8f2b9962-fa46-11e8-8118-6c299560df60", "path": "default/8f2b9962-fa46-11e8-8118-6c299560df60", "filename": "input_group1.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 17:35:59", "_public_url": null}',1);
CREATE TABLE evaluation (
	id INTEGER NOT NULL, 
	score FLOAT NOT NULL, 
	from_student_id INTEGER NOT NULL, 
	to_student_id INTEGER NOT NULL, 
	group_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(from_student_id) REFERENCES user (id), 
	FOREIGN KEY(to_student_id) REFERENCES user (id), 
	FOREIGN KEY(group_id) REFERENCES "group" (id)
);
INSERT INTO evaluation VALUES(1,1.198422741861530083,28263,28263,10);
INSERT INTO evaluation VALUES(2,0.394681338835397022,28263,28264,10);
INSERT INTO evaluation VALUES(3,1.11974323704723,28263,28268,10);
CREATE TABLE output (
	id INTEGER NOT NULL, 
	score NUMERIC NOT NULL, 
	data VARCHAR(4000) NOT NULL, 
	verification VARCHAR(8) NOT NULL, 
	ground_truth VARCHAR(8) NOT NULL, 
	active BOOLEAN NOT NULL, 
	original BOOLEAN NOT NULL, 
	use_ground_truth BOOLEAN NOT NULL, 
	input_id INTEGER NOT NULL, 
	group_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT verificationstatus CHECK (verification IN ('waiting', 'accepted', 'rejected')), 
	CONSTRAINT verificationstatus CHECK (ground_truth IN ('waiting', 'accepted', 'rejected')), 
	CHECK (active IN (0, 1)), 
	CHECK (original IN (0, 1)), 
	CHECK (use_ground_truth IN (0, 1)), 
	FOREIGN KEY(input_id) REFERENCES input (id), 
	FOREIGN KEY(group_id) REFERENCES "group" (id)
);
INSERT INTO output VALUES(1,16,'{"depot_name": "default", "files": ["default/e9de5ff0-fa39-11e8-8118-6c299560df60"], "file_id": "e9de5ff0-fa39-11e8-8118-6c299560df60", "path": "default/e9de5ff0-fa39-11e8-8118-6c299560df60", "filename": "output_from_4_to_4.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:05:27", "_public_url": null}','accepted','accepted',1,1,0,3,4);
INSERT INTO output VALUES(2,16,'{"depot_name": "default", "files": ["default/eec78fd2-fa39-11e8-8118-6c299560df60"], "file_id": "eec78fd2-fa39-11e8-8118-6c299560df60", "path": "default/eec78fd2-fa39-11e8-8118-6c299560df60", "filename": "output_from_4_to_5.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:05:36", "_public_url": null}','waiting','accepted',1,1,0,4,4);
INSERT INTO output VALUES(3,16,'{"depot_name": "default", "files": ["default/f3b6f53c-fa39-11e8-8118-6c299560df60"], "file_id": "f3b6f53c-fa39-11e8-8118-6c299560df60", "path": "default/f3b6f53c-fa39-11e8-8118-6c299560df60", "filename": "output_from_4_to_6.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:05:44", "_public_url": null}','waiting','accepted',1,1,0,5,4);
INSERT INTO output VALUES(4,15,'{"depot_name": "default", "files": ["default/0ada84fe-fa3a-11e8-8118-6c299560df60"], "file_id": "0ada84fe-fa3a-11e8-8118-6c299560df60", "path": "default/0ada84fe-fa3a-11e8-8118-6c299560df60", "filename": "output_from_5_to_4.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:06:23", "_public_url": null}','rejected','rejected',1,1,0,3,5);
INSERT INTO output VALUES(5,16,'{"depot_name": "default", "files": ["default/0d85e5ae-fa3a-11e8-8118-6c299560df60"], "file_id": "0d85e5ae-fa3a-11e8-8118-6c299560df60", "path": "default/0d85e5ae-fa3a-11e8-8118-6c299560df60", "filename": "output_from_5_to_5.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:06:27", "_public_url": null}','waiting','accepted',1,1,0,4,5);
INSERT INTO output VALUES(6,16,'{"depot_name": "default", "files": ["default/0fb5a9b8-fa3a-11e8-8118-6c299560df60"], "file_id": "0fb5a9b8-fa3a-11e8-8118-6c299560df60", "path": "default/0fb5a9b8-fa3a-11e8-8118-6c299560df60", "filename": "output_from_5_to_6.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:06:31", "_public_url": null}','waiting','accepted',1,1,0,5,5);
INSERT INTO output VALUES(7,16,'{"depot_name": "default", "files": ["default/22e0a31c-fa3a-11e8-8118-6c299560df60"], "file_id": "22e0a31c-fa3a-11e8-8118-6c299560df60", "path": "default/22e0a31c-fa3a-11e8-8118-6c299560df60", "filename": "output_from_6_to_4.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:07:03", "_public_url": null}','accepted','rejected',1,1,0,3,6);
INSERT INTO output VALUES(8,16,'{"depot_name": "default", "files": ["default/25dd3ce2-fa3a-11e8-8118-6c299560df60"], "file_id": "25dd3ce2-fa3a-11e8-8118-6c299560df60", "path": "default/25dd3ce2-fa3a-11e8-8118-6c299560df60", "filename": "output_from_6_to_5.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:07:08", "_public_url": null}','waiting','rejected',1,1,0,4,6);
INSERT INTO output VALUES(9,16,'{"depot_name": "default", "files": ["default/283d7e34-fa3a-11e8-8118-6c299560df60"], "file_id": "283d7e34-fa3a-11e8-8118-6c299560df60", "path": "default/283d7e34-fa3a-11e8-8118-6c299560df60", "filename": "output_from_6_to_6.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:07:12", "_public_url": null}','waiting','accepted',1,1,0,5,6);
INSERT INTO output VALUES(10,15,'{"depot_name": "default", "files": ["default/33bf3644-fa3a-11e8-8118-6c299560df60"], "file_id": "33bf3644-fa3a-11e8-8118-6c299560df60", "path": "default/33bf3644-fa3a-11e8-8118-6c299560df60", "filename": "output_from_7_to_7.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:07:31", "_public_url": null}','accepted','rejected',1,1,0,6,7);
INSERT INTO output VALUES(11,16,'{"depot_name": "default", "files": ["default/35b8fc82-fa3a-11e8-8118-6c299560df60"], "file_id": "35b8fc82-fa3a-11e8-8118-6c299560df60", "path": "default/35b8fc82-fa3a-11e8-8118-6c299560df60", "filename": "output_from_7_to_8.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:07:35", "_public_url": null}','rejected','accepted',1,1,1,7,7);
INSERT INTO output VALUES(12,16,'{"depot_name": "default", "files": ["default/377d1db4-fa3a-11e8-8118-6c299560df60"], "file_id": "377d1db4-fa3a-11e8-8118-6c299560df60", "path": "default/377d1db4-fa3a-11e8-8118-6c299560df60", "filename": "output_from_7_to_9.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:07:38", "_public_url": null}','accepted','accepted',1,1,0,10,7);
INSERT INTO output VALUES(13,16,'{"depot_name": "default", "files": ["default/3ef7b9fa-fa3a-11e8-8118-6c299560df60"], "file_id": "3ef7b9fa-fa3a-11e8-8118-6c299560df60", "path": "default/3ef7b9fa-fa3a-11e8-8118-6c299560df60", "filename": "output_from_8_to_7.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:07:50", "_public_url": null}','rejected','rejected',1,1,0,6,8);
INSERT INTO output VALUES(14,16,'{"depot_name": "default", "files": ["default/413882da-fa3a-11e8-8118-6c299560df60"], "file_id": "413882da-fa3a-11e8-8118-6c299560df60", "path": "default/413882da-fa3a-11e8-8118-6c299560df60", "filename": "output_from_8_to_8.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:07:54", "_public_url": null}','rejected','accepted',1,1,0,7,8);
INSERT INTO output VALUES(15,16,'{"depot_name": "default", "files": ["default/44002072-fa3a-11e8-8118-6c299560df60"], "file_id": "44002072-fa3a-11e8-8118-6c299560df60", "path": "default/44002072-fa3a-11e8-8118-6c299560df60", "filename": "output_from_8_to_9.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:07:59", "_public_url": null}','accepted','accepted',1,1,0,10,8);
INSERT INTO output VALUES(16,40,'{"depot_name": "default", "files": ["default/619d362e-fa3a-11e8-8118-6c299560df60"], "file_id": "619d362e-fa3a-11e8-8118-6c299560df60", "path": "default/619d362e-fa3a-11e8-8118-6c299560df60", "filename": "output_from_9_to_7.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:08:48", "_public_url": null}','accepted','rejected',1,1,0,6,9);
INSERT INTO output VALUES(17,16,'{"depot_name": "default", "files": ["default/63e65b40-fa3a-11e8-8118-6c299560df60"], "file_id": "63e65b40-fa3a-11e8-8118-6c299560df60", "path": "default/63e65b40-fa3a-11e8-8118-6c299560df60", "filename": "output_from_9_to_8.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:08:52", "_public_url": null}','accepted','rejected',1,1,0,7,9);
INSERT INTO output VALUES(18,16,'{"depot_name": "default", "files": ["default/68ed2da8-fa3a-11e8-8118-6c299560df60"], "file_id": "68ed2da8-fa3a-11e8-8118-6c299560df60", "path": "default/68ed2da8-fa3a-11e8-8118-6c299560df60", "filename": "output_from_9_to_9.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:09:01", "_public_url": null}','accepted','rejected',1,1,0,10,9);
INSERT INTO output VALUES(19,16,'{"depot_name": "default", "files": ["default/73efd14c-fa3a-11e8-8118-6c299560df60"], "file_id": "73efd14c-fa3a-11e8-8118-6c299560df60", "path": "default/73efd14c-fa3a-11e8-8118-6c299560df60", "filename": "output_from_10_to_10.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:09:19", "_public_url": null}','accepted','accepted',1,1,1,8,10);
INSERT INTO output VALUES(20,16,'{"depot_name": "default", "files": ["default/75c8fcf0-fa3a-11e8-8118-6c299560df60"], "file_id": "75c8fcf0-fa3a-11e8-8118-6c299560df60", "path": "default/75c8fcf0-fa3a-11e8-8118-6c299560df60", "filename": "output_from_10_to_11.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:09:22", "_public_url": null}','accepted','accepted',1,1,0,9,10);
INSERT INTO output VALUES(21,16,'{"depot_name": "default", "files": ["default/7db31e1e-fa3a-11e8-8118-6c299560df60"], "file_id": "7db31e1e-fa3a-11e8-8118-6c299560df60", "path": "default/7db31e1e-fa3a-11e8-8118-6c299560df60", "filename": "output_from_11_to_10.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:09:35", "_public_url": null}','rejected','accepted',1,1,0,8,11);
INSERT INTO output VALUES(22,16,'{"depot_name": "default", "files": ["default/7ff48ffa-fa3a-11e8-8118-6c299560df60"], "file_id": "7ff48ffa-fa3a-11e8-8118-6c299560df60", "path": "default/7ff48ffa-fa3a-11e8-8118-6c299560df60", "filename": "output_from_11_to_11.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 16:09:39", "_public_url": null}','accepted','rejected',1,1,0,9,11);
INSERT INTO output VALUES(23,16,'{"depot_name": "default", "files": ["default/de590998-fa46-11e8-8118-6c299560df60"], "file_id": "de590998-fa46-11e8-8118-6c299560df60", "path": "default/de590998-fa46-11e8-8118-6c299560df60", "filename": "output_from_2_to_2.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 17:38:11", "_public_url": null}','waiting','accepted',1,1,0,1,2);
INSERT INTO output VALUES(24,16,'{"depot_name": "default", "files": ["default/f13edaec-fa46-11e8-8118-6c299560df60"], "file_id": "f13edaec-fa46-11e8-8118-6c299560df60", "path": "default/f13edaec-fa46-11e8-8118-6c299560df60", "filename": "output_from_2_to_3.txt", "content_type": "application/octet-stream", "uploaded_at": "2018-12-07 17:38:43", "_public_url": null}','waiting','rejected',1,1,0,2,2);
CREATE TABLE protest (
	id INTEGER NOT NULL, 
	message VARCHAR(1000) NOT NULL, 
	accepted BOOLEAN NOT NULL, 
	submitter_id INTEGER NOT NULL, 
	output_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CHECK (accepted IN (0, 1)), 
	FOREIGN KEY(submitter_id) REFERENCES "group" (id), 
	FOREIGN KEY(output_id) REFERENCES output (id)
);
INSERT INTO protest VALUES(1,'rshnetar eahnstrh oeasn ohesnatr',0,10,19);
CREATE TABLE migrate_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT migrate_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO migrate_version VALUES('6f7d3e38c4d2');
COMMIT;
