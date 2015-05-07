#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from StringIO import StringIO
from colorama import init
from colorama import Fore, Back, Style
from pyvirtualdisplay import Display
import lxml.html
import time
import re
import requests
import argparse
import sys
import os
import sqlite3
import datetime

init(autoreset=True)

print "-----------------------------------------------------------------------------"
print "          Facebook group crawler - by Doghyun Seo"
print "-----------------------------------------------------------------------------"
print "Examples:"
print "1. Generates Group Member List:"
print "python fb-hfc.py -username '<username>'  -password '<password>' \n-query '<graph search query>' -group <name=url=id>"
print "-----------------------------------------------------------------------------"

# 입력 값 파싱
parser = argparse.ArgumentParser(usage="-h for full usage")
parser.add_argument('-username', dest="username", help='facebook username to login with (e.g. example@example.com)',required=True)
parser.add_argument('-password', dest="password", help='facebook password to login with (e.g. \'password\')',required=True)

parser.add_argument('-query', dest="query", help='Run method',required=False)
parser.add_argument('-group', dest="group", help='group name, group url, group id (e.g. "name=url=id")',required=False)

args = parser.parse_args()

# 파싱된 입력 값 검증
if args.query is None:
	parser.error("You must give atleast one method -query")

if args.query and args.group is None:
	parser.error("-You must provide -group")

# DB 연결
def connect_db(group_id):

	con = sqlite3.connect('./db/'+group_id+'.db')
	# con = sqlite3.connect('./test/'+group_id+'.db')
	cur = con.cursor()
	query = "create table if not exists id_" + group_id + "_member (id text primary key not null , name text not null, date datetime not null)"
	cur.execute(query)
	return con, cur

# DB 해제
def disconnect_db(db):

	db[1].close()
	db[0].commit()
	db[0].close()

# 로그 작성
def log_write(log):
	f = open("./source/log.txt", 'a')
	# f = open("log_test.txt", 'a')
	f.write("[%s] %s\n" % (time.ctime(), log))
	f.write("-"*80+'\n')
	f.close()

# 상태 로그 작성
def status_member_write(dic):
	f = open("./source/status_member.txt", 'a')
	# f = open("status_member_test.txt", 'a')
	f.write("[%20s] : %s\n" % ("Group Name", dic['group_name']))
	f.write("[%20s] : %s\n" % ("Group URL", dic['group_url']))
	f.write("[%20s] : %s\n" % ("Group Id", dic['group_id']))
	f.write("[%20s] : %s\n" % ("Start Time", dic['start_time']))
	f.write("[%20s] : %s\n" % ("End Time", dic['end_time']))
	f.write("[%20s] : %s\n" % ("Elapsed Time", dic['el_time']))
	f.write("[%20s] : %s\n" % ("Params Results", dic['params_results']))
	f.write("[%20s] : %s\n" % ("Data Len", dic['data_len']))
	f.write("[%20s] : %s\n" % ("Success", dic['success']))
	f.write("-"*80+'\n')
	f.close()

# 주어진 시간과 현재 시간의 차이 값 반환
def elapsed_time(sdate):
    e = datetime.datetime.now()
    if not sdate or len(sdate) < 14: return 0,0,0,0
    s = datetime.datetime(int(sdate[:4]), int(sdate[4:6]), int(sdate[6:8]), int(sdate[8:10]), int(sdate[10:12]), int(sdate[12:14]))
    days = (e-s).days
    sec = (e-s).seconds
    hour, sec = divmod(sec, 3600)
    minute, sec = divmod(sec, 60)
    return days, hour, minute, sec

# 페이스북 로그인
def facebook_login(username,password):
	print ("\nLogin to Facebook...."),
	log_write("<Init>Login to Facebook....\n")

	sys.stdout.flush() 
	url = "http://www.facebook.com"
	driver.get(url)
	elem = driver.find_element_by_id("email")
	elem.send_keys(username)
	elem = driver.find_element_by_id("pass")
	elem.send_keys(password)
	elem.send_keys(Keys.RETURN)
	time.sleep(1)
	html_source = driver.page_source
	if "Please re-enter your password" in html_source or "Incorrect Email" in html_source:
		print Fore.RED + "Incorrect Username or Password"
		log_write("<Init>Incorrect Username or Password\n")
		driver.close()
		exit()
	else:
		print Fore.GREEN + "Success\n"
		log_write("<Init>Success\n")
	return driver.get_cookies()

# 페이스북 그룹 멤버 크롤링
def group_member(cur, group):

	group_name = group[0]
	group_url = group[1]
	group_id = group[2]

	# 상태 파일 저장을 위한 초기화
	status_dic = {}
	status_dic['group_name'] = group_name
	status_dic['group_url'] = group_url
	status_dic['group_id'] = group_id

	status_dic['start_time'] = time.ctime()
	start_sdate = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) 

	print "\n<Member, Start>Parsing Group : " + Fore.YELLOW + group_name + "\n"
	log_write("<Member, Start>Parsing Group : "+ group_name + "\n")

	# 크롤링할 주소
	graph_search_query = "https://www.facebook.com/groups/"+group_url+"/members"

	data = list()
	driver.get(graph_search_query)

	elem = driver.get(graph_search_query)

	while 1:
		time.sleep(5)
		try:
			# 더 보기 클릭
			elem = driver.find_element_by_xpath(".//a[@class='pam uiBoxLightblue uiMorePagerPrimary']")
			elem.click()
		except:
			break

	# 파싱할 요소
	xpath_name_params1 = ".//div[@class='fsl fwb fcb']/a/@href"		# 아이디 값
	xpath_name_params2 = ".//div[@class='fsl fwb fcb']/a/text()"	# 이름 값
	xpath_name_params3 = ".//div[@class='fsm fwn fcg']/abbr/@title"	# 가입 

	html_source = driver.page_source

	html_lxml = lxml.html.parse(StringIO(html_source))				# parse to lxml object
	params_result1 = html_lxml.xpath(xpath_name_params1)
	params_result2 = html_lxml.xpath(xpath_name_params2)
	params_result3 = html_lxml.xpath(xpath_name_params3)

	params_results = str(len(params_result1)) +", "+ str(len(params_result2)) +", "+ str(len(params_result3))
	print "<Member, Parsing> Param Results : " + params_results + "\n"
	log_write("<Member, Parsing> Param Results : " + params_results + "\n")
	status_dic['params_results'] = params_results

	# ID 값을 추출하기
	params_result1_res = list()
	for param in params_result1:
			if "profile.php" in param:
				result = re.search('(?<=\profile\.php\?id=)(.*\n?)(?=&fref=grp_mmbr_list)', param)
				if result.group() not in data:
					params_result1_res.append(result.group())
			else:
				result = re.search('(?<=\.com\/)(.*\n?)(?=\?)', param)
				if result.group() not in data:
					params_result1_res.append(result.group())

	data = zip(params_result1_res, params_result2, params_result3)
	data_len = len(data)
	print "<Member, Parsing> Data Len : " + str(data_len) + "\n"
	log_write("<Member, Parsing> Data Len : " + str(data_len) + "\n")
	status_dic['data_len'] = str(data_len)

	success = 0;

	# DB에 입력
	for param in data:
		cur.execute("select count(*) from id_" + group_id + "_member where id = '" + param[0] + "'")
		for row in cur:
			if not (row[0]>0):
				param1_en = param[1].encode("UTF-8").replace("'", "''")
				param2_en = param[2].encode("UTF-8")
				if len(param2_en) > 40:
					param2_en = param2_en.replace("년 ","-").replace("월 ","-").replace("일"," ")[0:11].strip()
				else :
					param2_en = param2_en.replace("년 ","-").replace("월 ","-").replace("일"," ")[0:10].strip()
				cur.execute("insert into id_"+ group_id + "_member(id, name, date) values ('"+param[0]+"', '"+param1_en+"', '"+param2_en+"')")
				success = success + 1

	print "<Member, Parsing> Success In Database : " + str(success) + "\n"
	log_write("<Member, Parsing> Success In Database : " + str(success) + "\n")
	status_dic['success'] = str(success)

	status_dic['end_time'] = time.ctime()

	el_time = str(elapsed_time(start_sdate))

	print "<Member, Parsing> Elapsed Time : " + el_time + "\n"
	log_write("<Member, Parsing> Elapsed Time : " + el_time + "\n")
	status_dic['el_time'] = el_time


	print "<Member, End>Parsing Group : " + Fore.YELLOW + group_name + "\n"
	log_write("<Member, End>Parsing Group : "+ group_name + "\n")

	status_member_write(status_dic)

username = args.username
password = args.password

display = Display(visible=0, size=(1600, 900))
display.start()
driver = webdriver.Firefox()
cookies = dict()
cookies = facebook_login(username,password)

if args.query :
	group = args.group.replace('\n','').split('=')

	try:
		db = connect_db(group[2])
		group_member(db[1], group)
	except Exception, e:
		print (e)
		log_write("#####Error##### : " + str(e) + "\n")
	finally:
		disconnect_db(db)

driver.close()
exit()


