# Proxy_IP(代理IP池)
一个小型的代理IP池，同时也是对自己技术的一个总结规整，下面说一下项目吧。  

* Flask_test: 负责前端展示；
* proxy_ip: 代理IP抓取服务端(scrapyd)主目录;
* proxy_spider: 代理IP抓取代码(scrapy);
* spiderkeeper: 顾名思义配合 scrapyd 使用的定时调度组件；

***
## 项目的整体流程：
scrapy(爬虫) + scrapyd + spiderkeeeper + docker(redis) + flask + uwsgi + docker(nginx);  
***项目启动：Flask_test、proxy_ip、spiderkeeper 每个文件夹下的 .sh 文件 为程序开关；***

## 基础环境：
Linux(CentOS or Ubuntu)；  
python(virtualenv) 虚拟环境，这里本来打算用 Anaconda 但是后来因为 有两个虚拟环境的原因，放弃使用 Anaconda ， python -Version == 3.6 ，**这里虚拟环境强烈建议将 spiderkeeper 独立出来，spiderkeeper 与 scrapyd 放在一个虚拟环境应该会因为版本问题导致一下依赖不兼容，我的是这样的，仅供参考**；  
Docker 最新本(版本迭代比较快，主要以学习为主)；  
***
下面分享一下项目中注意点，毕竟技术浅薄，如有不对留言指正。

### proxy_spider:
Scrapy 爬虫代码；  
middlewares 的编写，这里我加代理 IP 的时候没有单独加一个中间件，当然单独加一个代理中间件也是可以的(我的代理请求头是放在单独的中间件，这个网上大部分帖子都是单独放一个代理IP的中间件吧，有需要的朋友可以改一下)，具体的代码逻辑请移步 .py 文件；  
pipelines 的编写， 本来想把 redis 嵌套在 pipelines 去进行交互，但是没有找到很好的办法去替代 redis 连接池的效果， 如果朋友们有好的方法，可以教我一下，非常感谢， 所以这里单独写了一个 redis 交互的 .py 文件；  
settings 的编写，是一些具体配置信息，详情可见 .py 文件；  
**同时，还用到了 scrapy_splash 这个 scrapy 插件 用在 站大爷代理 这个站点，但是由于目前技术原因(要涉及到验证码 ocr 识别端口，由于一下简单的灰度、去噪，处理的不太好，打算用更高深的技术去搞一下，所以先放一放)。其他爬虫并没有用到这个插件，所以可以自动忽略。还有一个爬虫站点是 66免费代理 这个网站，在我的服务器上没有跑起来，有研究过，但是好像超出能力范围，初步怀疑是因为境外 IP 访问一些国内网站，会被一些个别网站过滤，或者一些别的原因，还在研究。当然境内 IP 去访问是没问题的；**  
***最后一点，爬虫的 Xpath、 URL 等 有可能会变动，这个要根据网站页面实时更改。***

### proxy_ip：
scrapyd 服务端，项目的一下主要程序代码(日志清理、redis 废弃的代理定期清理等程序，当然这个是要加定时清理任务的，具体操作可以网上了解一下 **Linux crontab**), 由于我的服务器只有40G的系统盘，所有我也没有把 scrapyd 输出的日志保存到文件里，当然我承认这是一个很不好的习惯，但是没办法呀，因为贫穷只能阉割咯，这里问题的难点在于，如何做到让 scrapyd 与 nginx 一样可以不停机情况下重载配置、日志文件等，我觉得是有办法解决的，但是以我目前的能力，还需要在学习一下。

### spiderkeeper：
spiderkeeper 客户端，由于我是单独一个虚拟环境，所以索性也单独一个文件夹，输出日志同 scrapyd 一样，具体移步文件夹下的启动文件。

### Flask_test：  
Flask框架、uwsgi 等，由于不是一个前端人员，就简单搞了一个前端页面显示一下，启动文件 .sh 文件，这里 uwsgi.ini 配置文件时，由于我的 nginx 是 docker 的， 所以 socket 的 ip 是 docker 桥接局域网的ip，我个人理解就是，用电脑开了一个热点，如果想让连接热点的手机链到开热点的电脑，就需要当前热点的网关，这个是个人理解，如有不对请留言指正。当然也可以不用 docker 或者在创建 容器时，映射一个地址。uwsgi.ini 配置文件其他参数可以在网上搜到。还有 uwsgi.log 我没有做日志分割，想做的也可以做一下。

### Docker：  
docker nginx 搭建网上也是有教程的，这里附上一份 .conf 文件仅供参考。

```conf
server {
    listen       80 default_server;
    server_name  0.0.0.0;	# 公网地址 IP ，也可以是本地地址

    #动态请求
    location / {
        include uwsgi_params;
        uwsgi_pass 172.17.0.1:8000; 	# 这里转接给 uwsgi (开热点的电脑)
    }
}

```

docker redis 就是简单拉取一个镜像，做了一些简单的配置。

```conf
#bind 127.0.0.1
protected-mode no
daemonize no
appendonly yes
requirepass *******   # 密码
```

## End  

最后说一下，环境搭好还要打包 proxy_spider 为 .egg 文件上传到 scrapyd 加定时任务使用，这里你也可以选择其他组件，替换掉 spiderkeeper 也可以，简单折腾，如有不对，请留言指正。
