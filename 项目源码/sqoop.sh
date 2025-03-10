cd /opt/module/sqoop-1.4.6
bin/sqoop export --connect jdbc:mysql://192.168.10.103:3306/covid_19 --username root --password 123456 --table city_info --export-dir '/user/hive/warehouse/covid_19.db/city_info' --input-fields-terminated-by '\001'

bin/sqoop export --connect jdbc:mysql://192.168.10.103:3306/covid_19 --username root --password 123456 --table city_data --export-dir '/user/hive/warehouse/covid_19.db/city_data' 
--input-fields-terminated-by '\001'

