#fb-group-crawler

##Facebook Group Crawler

[참조](https://github.com/prili/fb-hfc)를 참조하여 작성하였습니다.
우분투 및 OSX 에서만 작동하는 것을 확인했습니다.

## 설치

``` bash
apt-get install python-lxml
pip install -r requirements.txt
```

## 실행

### 직접 실행

```python
python fb-hfc.py -username '<username>'  -password '<password>' -query '<graph search query>' -group <name=url=id>
```

username: Facebook ID
password: Facebook PW
query : Member
group : 그룹별명=그룹주소=그룹ID

그룹 아이디는 [Lookup-ID](http://lookup-id.com)라는 사이트를 이용할 수 있습니다.

### Shell을 통한 실행

```bash
#!/bin/bash

username=
password=

cat ./source/group_list.txt | \
while read line
do
	echo -e "\n\n\n $line"
	python fb-crawler.py -username $username -password $password -query member -group $line

    pids=$(pidof /usr/bin/Xvfb)
	echo "Xvfb pids : $pids"
	kill $pids
	ps
done
```

username: Facebook ID
password: Facebook PW

상단의 값을 입력 후 하위폴더 source에 그룹의 리스트를

	name=url=id
	name=url=id

와 같이 작성하면 됩니다.

## 한계

멤버수가 8000~9000명인 그룹의 경우 데이터가 정확하지 않으며, 9000명이상인 그룹에서는 그 이상의 데이터를 가져올 수가 없습니다.