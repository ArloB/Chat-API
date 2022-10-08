create table users (
  id serial,
  email varchar(40) not null unique,
  password text not null,
  first_name varchar(15) not null,
  last_name varchar(15) not null,
  handle varchar(20) DEFAULT '',
  profile_image text DEFAULT '',
  owner bool DEFAULT false,
  iat integer,
  primary key (id)
);

create table channels (
  id serial,
  public bool DEFAULT true,
  name varchar(30) not null,
  primary key (id)
);

create table channel_users (
  channel_id integer,
  user_id integer,
  admin bool DEFAULT false,
  foreign key (channel_id) references channels(id),
  foreign key (user_id) references users(id),
  primary key (channel_id, user_id)
);

create table messages (
  id serial,
  channel_id integer not null,
  user_id integer not null,
  message text not null,
  time integer not null,
  pinned bool DEFAULT false,
  foreign key (channel_id) references channels(id),
  foreign key (user_id) references users(id),
  primary key (id)
);

create table reacts (
  user_id integer,
  message_id integer,
  type integer DEFAULT 1,
  foreign key (user_id) references users(id),
  foreign key (message_id) references messages(id),
  primary key (user_id, message_id)
);

insert into users (email, password, first_name, last_name, owner)
values ('admin@admin.com', 'password', 'admin', 'admin', true);