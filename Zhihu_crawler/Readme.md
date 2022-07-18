
# 实现说明

因hint中提供的接口需要提供登录cookie才能获取数据，所以本次知乎热榜获取采取另外一个接口实现，直接获取对应数据json，因此热度数据可能有所区别。excerpt通过具体的question页面获取。

# 安装需求
本次爬虫需要安装requests，bs4

```
pip install requests
pip install bs4
```


