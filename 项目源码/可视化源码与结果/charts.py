import pandas as pd

import collections
from pyecharts.charts import WordCloud, Bar, Pie, Page, EffectScatter
from pyecharts.globals import ThemeType
import pyecharts.options as opts
from pyecharts.components import Table
from pprint import pprint




theme_config = ThemeType.CHALK
#  表格和标的顾色
table_color = ''
if theme_config == ThemeType.DARK:
    table_color = '#333333'
elif theme_config == ThemeType.CHALK:
    table_color = '#293441'
elif theme_config == ThemeType.PURPLE_PASSION:
    table_color = '#5B5C6E'
elif theme_config == ThemeType.PURPLE_PASSION:
    table_color = '#F8E8C0'
elif theme_config == ThemeType.ESSOS:
    table_color ='#F0F0F5'
else:
    table_color = ''





import pymysql as mysql
import pandas as pd
import matplotlib.pyplot as plt 
import pyecharts.options as opts

from pyecharts.globals import ThemeType
from pyecharts.charts import Map, Timeline, Page, Line
from pyecharts.faker import Faker
import os

con = mysql.connect(host="192.168.10.103",port=3306,user="root",passwd="123456",db="covid_19",charset="utf8mb4")
mycursor = con.cursor()
print("Connect successful!!")

def render_line():
    # select sql
    sql = "select city_zipCode, updatetime, city_confirmedCount from city_data where city_zipCode in (select city_zipCode from city_info where provinceChineseName='黑龙江省')   order by updatetime asc;"
    data = pd.read_sql(sql,con=con)
    print(data.head())

    # line
    line = Line(init_opts=opts.InitOpts(theme=theme_config))
    
    # x
    line.add_xaxis( data.updatetime.drop_duplicates().to_list())
    
    # each y
    
    for id in data.city_zipCode.drop_duplicates().to_list():
        #if len(data.city_zipCode[data.city_zipCode==id])>=30:
        line.add_yaxis(id, data[data.city_zipCode==id].city_confirmedCount)
    
    # piture configuration
    line.set_global_opts(
        title_opts=opts.TitleOpts(title="city_confirmedCount"),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
    )
    return line
    


def render_map():
    # select sql
    sql = "select updatetime, concat(cityChineseName,'市') as cityChineseName, city_confirmedCount from city_data join city_info on city_data.city_zipCode=city_info.city_zipCode where provinceChineseName='黑龙江省' and (updatetime like '202_-%-01%' or updatetime like '202_-%-15%') order by updatetime,cityChineseName;"
    data = pd.read_sql(sql,con=con)
    print(data.head())
    
    df=data
    sj=list(data['updatetime'])
    
    timeline = Timeline(init_opts=opts.InitOpts(theme=theme_config,width='720px', height='350px'))
    
    for m in range(len(sj)):
        map=(
            Map()
            .add("黑龙江", 
                 [list(z) for z in zip(data[data.updatetime==sj[m]].cityChineseName, data[data.updatetime==sj[m]].city_confirmedCount)], 
                 "黑龙江")
            .set_global_opts(
                title_opts=opts.TitleOpts(title="黑龙江"), 
                visualmap_opts=opts.VisualMapOpts( 
                min_=0,
                max_=670,
                split_number = 10,
                is_piecewise=True,
                )))
        timeline.add(chart=map,time_point=sj[m])
        
    timeline.add_schema(is_auto_play=True, play_interval=0.01) 
    return timeline









def make_table():
    "绘制数据表格"
    # 标题
    
    sql = "select updatetime, concat(cityChineseName,'市') as cityChineseName, city_confirmedCount,city_suspectedCount,city_curedCount,city_deadCount from city_data join city_info on city_data.city_zipCode=city_info.city_zipCode where provinceChineseName='内蒙古自治区' and (updatetime like '202_-%-01%' or updatetime like '202_-%-15%') order by updatetime,cityChineseName limit 30;"
    data = pd.read_sql(sql,con=con)
    print(data.head())
    
    v_df=data
    
    attributes={"width":"450px", "height":"350px","padding": "20px","font-size":"10px","color":"#F0F8FF"}

    data_list = v_df.values.tolist()
    table = (
        Table(page_title='我的表格标题')
            .add(headers=['时间', '城市', '确诊人数', '疑似人数', '治愈人数', '死亡人数'], 
                 rows=data_list, 
                 attributes={
#                      "align": "left",
#                      "border": False,
#                      "padding": "20px",
                     "style": "background:{}; width:450px; height:350px; font-size:10px; color:#C0C0C0;padding:3px;".format(table_color)}
                )
            .set_global_opts(title_opts=opts.TitleOpts(title='这是表格1'))
    )
    table.render('表格.html')
    print('生成完毕:表格.html')
    return table




def make_top10_comment_bar():
    "TOP10评论数的作者-条形图"
    sql = "select distinct cityChineseName,city_confirmedCount from city_data join city_info on city_data.city_zipCode=city_info.city_zipCode where (updatetime like '2022-10-11%') order by city_confirmedCount desc limit 20;"
    data = pd.read_sql(sql,con=con)
    print(data.head())
    
    df_top10_comment = data
#     print(df_top10_comment)
    x_data = df_top10_comment['cityChineseName'].values.tolist()
    x_data.sort()
    y_data = df_top10_comment[ 'city_confirmedCount' ].values.tolist()
    y_data.sort()
    # 画条形图
    bar = Bar(
        init_opts=opts.InitOpts(theme=theme_config, width="450px", height="350px", chart_id='bar_cmt1'))  # 初始化条形图
    bar.add_xaxis(x_data)  # 增加x轴数据
    bar.add_yaxis("确诊数量", y_data)  # 增加y轴数据
    bar.reversal_axis()  # 设置水平方向
    bar.set_series_opts(label_opts=opts.LabelOpts(position="right"))  # Label出现位置
    bar.set_global_opts(
        legend_opts=opts.LegendOpts(pos_left='right'),
        title_opts=opts.TitleOpts(title="确诊数量-条形图", pos_left='center'),  # 标题
        toolbox_opts=opts.ToolboxOpts(is_show=False, ),  # 不显示工具箱
        xaxis_opts=opts.AxisOpts(name="城市",  # x轴名称
                                 axislabel_opts=opts.LabelOpts(font_size=8, rotate=0),
                                 splitline_opts=opts.SplitLineOpts(is_show=False)
                                 ),
        yaxis_opts=opts.AxisOpts(name="确诊数量",  # y轴名称
                                 axislabel_opts=opts.LabelOpts(font_size=7, rotate=45),  # y轴名称
                                 )
    )
    bar.render("确诊数量_条形图.html")  # 生成html文件
    print('生成完毕:确诊数量_条形图.html')
    return bar





def filmname_wordcloud():
    sql = "select distinct cityChineseName,city_confirmedCount from city_data join city_info on city_data.city_zipCode=city_info.city_zipCode where (updatetime like '2022-10-11%') order by city_confirmedCount desc limit 20;"
    data = pd.read_sql(sql,con=con)
    print(data['city_confirmedCount'].head())
    
    result=data['city_confirmedCount']
    
    data = collections.Counter(result)
    data = data.most_common(300)

    wc = WordCloud(init_opts=opts.InitOpts(width="450px", height="350px", theme=theme_config, chart_id='wc1'))
    wc.add(series_name="确诊数",
           data_pair=data,
           word_size_range=[15, 20],
           width='400px',  # 宽度
           height='300px',  # 高度
           word_gap=5  # 单词间隔
           )  # 增加数据
    wc.set_global_opts(
        title_opts=opts.TitleOpts(pos_left='center',
                                  title="确诊最多人数-词云图",
                                  title_textstyle_opts=opts.TextStyleOpts(font_size=20)  # 设置标题
                                  ),
        tooltip_opts=opts.TooltipOpts(is_show=True),  # 不显示工具箱
    )
    wc.set_series_opts(label_opts=opts.LabelOpts(is_show=True))
    wc.render('确诊_词云图.html')  # 生成html文件
    print('生成完毕:确诊_词云图.html')
    return wc







def make_analyse_pie():
    
    sql = "select city_info.cityChineseName,city_confirmedCount from city_data join city_info on city_data.city_zipCode=city_info.city_zipCode where (updatetime like '2022-10-11%') and provinceChineseName='北京市';"
    data = pd.read_sql(sql,con=con)
    print(data.head())
   
    pie = (
        Pie(init_opts=opts.InitOpts(theme=theme_config, width="600px", height="350px", chart_id='pie1'))
            .add(series_name="北京-饼图",  # 系列名称
                 data_pair= data.values.tolist(),
                 rosetype="radius",  # 是否展示成南丁格尔图
                 radius=["30%", "55%"],  # 扇区圆心角展现数据的百分比，半径展现数据的大小
                 )  # 加入数据
            .set_global_opts(  # 全局设置项
            title_opts=opts.TitleOpts(title="北京-饼图", pos_left='center'),  # 标题
            legend_opts=opts.LegendOpts(pos_left='right', orient='vertical')  # 图例设置项,靠右,竖向排列
        )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}")))  # 样式设置项
    pie.render('北京-饼图.html')  # 生成html文件
    print('生成完毕:北京-饼图.html')
    return pie




def make_title(v_title):
    table = Table()
    table.add(headers=[v_title], rows=[], 
              attributes={

        "style": "background:{}; width:1350px; height:50px; font-size:25px; color:#C0C0C0;".format(table_color)
    }
             )
    table.render('大标题.html')
    print('生成完毕:大标题.html')
    return table




def Page_total():
    page = (
        Page(layout=Page.DraggablePageLayout)
            .add(
            make_title('基于Hive的疫情数据大屏展示'),
            render_map(),
            render_line(),
            make_table(),
            filmname_wordcloud(),
            make_top10_comment_bar(),
            make_analyse_pie(),
        )
    )
    page.render('page.html')

Page_total()