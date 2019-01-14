
# coding: utf-8

# In[15]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import datetime 
import pymysql


# In[16]:


def save_DB(total_list) : 
    conn = pymysql.connect(host = "147.43.122.131", user = "root", password = "1234", charset = "utf8mb4")
    curs = conn.cursor()
    
    curs.execute("use daum_blog ;")

    query = """CREATE TABLE IF NOT EXISTS """+ keyword+ """(ID int, URL varchar(100), Title varchar(100), Date varchar(20), Writer varchar(50), blog_like int, Count int,Text longtext);"""
    curs.execute(query)

    query = """ALTER TABLE """ + keyword +""" CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"""
    curs.execute(query)

    conn.commit()
    
    select_query = """SELECT * from """ + keyword 
    index = curs.execute(select_query)

    for value in total_list :
        url = value[0]
        title = value[1]
        date = value[2]
        writer = value[3]
        like = value[4]
        count = value[5]
        content = value[6]
        
        query = """insert into """ + keyword + """(ID, URL, Title, Date, Writer, blog_like, Count, Text) values (%s, %s, %s, %s, %s, %s, %s, %s) ; """
        curs.execute(query, (str(index), url, title, date,writer,like,count,content))

        index = index + 1 

        conn.commit()
        
    conn.close()
    print("FINISH")


# In[17]:


keyword = input("Keyword ? ")

start_year = input("Start Year ? ")
start_month = input("Start Month ? ")
start_day = input("Start Day ? ")

end_year = input("End Year ? ")
end_month = input("End Month ? ")
end_day = input("End Day ? ")

start_date = start_year+start_month+start_day
end_date = end_year+end_month+end_day


# In[18]:


options = webdriver.ChromeOptions()
options.add_argument('headless')
dt_start_date = datetime.datetime.strptime(start_date,"%Y%m%d").date()
dt_end_date = datetime.datetime.strptime(end_date,"%Y%m%d").date()
day_1 = datetime.timedelta(days=1)
dt_start_1 = dt_start_date

# 일수를 하루씩 잘라서 반복
while dt_start_1 <= dt_end_date :
    total_list = []
    URL_date_list = []
    page_num = 1
    print(dt_start_1)
    # 페이지 만큼 돌면서 링크 수집
    while True : 
        p_url = 'https://search.daum.net/search?w=blog&m=board&lpp=10&DA=STC&q='+keyword+'&f=section&SA=daumsec&sd='+start_date+'000000&ed='+start_date+'235959&period=u&m=board&page='+str(page_num)
        driver = webdriver.Chrome('./chromedriver/chromedriver')
        driver.implicitly_wait(3)
        driver.get(p_url)
        
        soup = BeautifulSoup(driver.page_source,'html.parser')
        span_tags = soup.findAll("span", {"class" : "f_nb date"})
        a_tags = driver.find_elements_by_xpath("//a[@class='f_link_b']")
        
        element = soup.find("span",{"class" : "btn_page btn_next"})
            
        # 한 페이지에 있는 링크들 전부 가져오기
        for a,d in zip(a_tags,span_tags) :
            url = a.get_attribute("href")
            if 'blog.daum' in url :
                driver = webdriver.Chrome('./chromedriver/chromedriver')
                driver.implicitly_wait(3)
                driver.get(url)
                # 페이지 변환      
                frame = driver.find_element_by_name('BlogMain')
                driver.switch_to_frame(frame)
                soup = BeautifulSoup(driver.page_source,'html.parser')
                
                blog_title = soup.find("strong", {"class" : "cB_Title cB_TitleImage"}).text.replace('\n','').strip()
                blog_date = d.text
                writer = soup.find("span", {"class" : "cB_Name"}).text
                reply_count = driver.find_element_by_css_selector('#cContentBottom > div > ul > li').text.strip()[3:]
                # 페이지 변환 
                frame = driver.find_element_by_css_selector('#cContentBody > div > iframe')
                driver.switch_to_frame(frame)
                soup = BeautifulSoup(driver.page_source,'html.parser')

                # 공감 버튼이 아예 없거나 비어있다면 0으로
                if soup.find("span", {"class" : "num_empathy uoc-count"}) is not None :
                    if soup.find("span", {"class" : "num_empathy uoc-count"}).text : 
                        blog_like = soup.find("span", {"class" : "num_empathy uoc-count"}).text 
                    else :
                        blog_like = 0
                else :
                    blog_like = 0
                    
                blog_content = soup.find("div", {"id" : "contentDiv"}).text.replace('\n','').strip()

                total_list.append([url,blog_title,blog_date,writer,blog_like,reply_count,blog_content])
                
        # daum blog는 다음 버튼이 활성화일땐 a태그, 비활성화일땐 span태그가 페이지에 나타나도록 설계되어있음
        if element is None :
            page_num += 1
        else : 
            break;
            
     # 날짜 변환    
    dt_start_1 = dt_start_1 + day_1
    temp = str(dt_start_1)
    start_date = temp[:4]+temp[5:7]+temp[8:]
    
    save_DB(total_list)


# In[19]:


# conn = pymysql.connect(host = "", user = "root", password = "", charset = "utf8mb4")
# curs = conn.cursor()
# curs.execute("use daum_blog ;")
# query = """select * from 원자력; """
# curs.execute(query)
# all_rows = curs.fetchall()
# for i in all_rows:
#     print(i)


# In[ ]:


# DB 생성시 이용
# conn = pymysql.connect(host = "", user = "root", password = "", charset = "utf8mb4")
# curs = conn.cursor()
# query = """CREATE DATABASE daum_blog default CHARACTER SET UTF8;"""
# curs.execute(query)


# In[ ]:


# DB삭제시 이용
# conn = pymysql.connect(host = "", user = "root", password = "", charset = "utf8mb4")
# curs = conn.cursor()
# query = """DROP DATABASE daum_blog; """
# curs.execute(query)

