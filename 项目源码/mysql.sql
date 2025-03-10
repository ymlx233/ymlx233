create database covid_19;
show databases;
use covid_19;

#创建表
create table city_info(
city_zipCode char(10) not null comment 'city_zipCode' primary key,
cityEnglishName varchar(500),
cityChineseName varchar(500),
province_zipCode char(10) not null,
provinceEnglishName varchar(50),
provinceChineseName varchar(50)
);

#创建表
create table city_data(
city_zipCode char(10) not null comment 'city_zipCode',
city_confirmedCount int(10) not null default 0,
city_suspectedCount int(10) not null default 0,
city_curedCount int(10) not null default 0,
city_deadCount int(10) not null default 0,
updatetime date NOT NULL);