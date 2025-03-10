一、ODS 层
表名：ods_covid_data
存储原始数据，不做任何复杂的处理。
create external table if not exists ods_covid_data2 (
    continentName string,
    continentEnglishName string,
    countryName string,
    countryEnglishName string,
    provinceName string,
    provinceEnglishName string,
    province_zipCode string,
    province_confirmedCount int,
    province_suspectedCount int,
    province_curedCount int,
    province_deadCount int,
    updateTime string,
    cityName string,
    cityEnglishName string,
    city_zipCode string,
    city_confirmedCount int,
    city_suspectedCount int,
    city_curedCount int,
    city_deadCount int
)
row format delimited
fields terminated by '\t'
lines terminated by '\n'
stored as textfile
location '/user/hadoop/covid_19/ods/';

-- 加载数据
load data inpath '/user/hadoop/covid_19_warehouse/ods/DXYArea.csv' overwrite into table ods_covid_data2;

二、DWD 层
1. 表名：dwd_china_covid_filtered
过滤掉无效数据：
首行数据。
没有邮政编码或城市英文名为空的数据。
只保留中国的数据。
set hive.exec.reducers.bytes.per.reducer=256000000;  # 设为 256 MB

create table if not exists dwd_china_covid_filtered as
select
    provinceEnglishName as provinceenglishname,
    provinceName as provincechinesename,
    province_zipCode as province_zipcode,
    updateTime as updatetime,
    cityEnglishName as cityenglishname,
    cityName as citychinesename,
    city_zipCode as city_zipcode,
    city_confirmedCount as city_confirmedcount,
    city_suspectedCount as city_suspectedcount,
    city_curedCount as city_curedcount,
    city_deadCount as city_deadcount
from ods_covid_data
where countryEnglishName = 'China'
  and city_zipCode is not null
  and trim(cityEnglishName) <> '';


2. 表名：dwd_china_covid_daily_max
基于 dwd_china_covid_filtered 表：
保留每个城市每天的数据中确诊数最多的一条记录。
使用 row_number() 实现去重。
create table if not exists dwd_china_covid_daily_max as
select
    provinceenglishname,
    provincechinesename,
    province_zipcode,
    updatetime,
    cityenglishname,
    citychinesename,
    city_zipcode,
    city_confirmedcount,
    city_suspectedcount,
    city_curedcount,
    city_deadcount
from (
    select 
        *,
        row_number() over (partition by city_zipcode, substr(updatetime, 1, 10) order by city_confirmedcount desc) as rank
    from dwd_china_covid_filtered
) t
where rank = 1;

三、DWS 层
1. 表名：dws_city_info
提取城市和省份的基础信息。
数据来源：dwd_china_covid_daily_max。
create table if not exists dws_city_info as
select 
    city_zipcode,
    cityenglishname,
    citychinesename,
    province_zipcode,
    provinceenglishname,
    provincechinesename
from dwd_china_covid_daily_max
group by 
    city_zipcode, 
    cityenglishname, 
    citychinesename, 
    province_zipcode, 
    provinceenglishname, 
    provincechinesename;

2. 表名：dws_city_daily_summary
汇总每天每个城市的疫情统计数据。
数据来源：dwd_china_covid_daily_max。
create table if not exists dws_city_daily_summary as
select 
    city_zipcode,
    substr(updatetime, 1, 10) as dt,
    sum(city_confirmedcount) as total_confirmed,
    sum(city_suspectedcount) as total_suspected,
    sum(city_curedcount) as total_cured,
    sum(city_deadcount) as total_dead
from dwd_china_covid_daily_max
group by city_zipcode, substr(updatetime, 1, 10);


3. 表名：dws_province_daily_summary
按省份汇总每天的数据。
create table if not exists dws_province_daily_summary as
select 
    province_zipcode,
    substr(updatetime, 1, 10) as dt,
    sum(city_confirmedcount) as total_confirmed,
    sum(city_suspectedcount) as total_suspected,
    sum(city_curedcount) as total_cured,
    sum(city_deadcount) as total_dead
from dwd_china_covid_daily_max
group by province_zipcode, substr(updatetime, 1, 10);



四、ADS 层
1. 表名：ads_city_trends
城市级别的趋势分析。
create table if not exists ads_city_trends as
select 
    city_zipcode,
    dt,
    total_confirmed,
    lag(total_confirmed) over (partition by city_zipcode order by dt) as confirmed_diff,
    total_cured,
    total_dead
from dws_city_daily_summary;


2. 表名：ads_province_ranking
按照某一天的累计确诊数对省份进行排名。
create table if not exists ads_province_ranking as
select 
    dt,
    province_zipcode,
    rank() over (partition by dt order by sum(total_confirmed) desc) as rank,
    sum(total_confirmed) as total_confirmed
from dws_province_daily_summary
group by dt, province_zipcode;

3. 表名：ads_national_summary
全国每日数据汇总。
create table if not exists ads_national_summary as
select 
    dt,
    sum(total_confirmed) as national_confirmed,
    sum(total_suspected) as national_suspected,
    sum(total_cured) as national_cured,
    sum(total_dead) as national_dead
from dws_province_daily_summary
group by dt;




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