[English](README.md) | 简体中文

## 说明
> 历史版本：
> [1.2.0](https://github.com/alibaba/havenask/tree/1.2.0),
> [1.1.0](https://github.com/alibaba/havenask/tree/1.1.0),
> [1.0.0](https://github.com/alibaba/havenask/tree/1.0.0),
> [1.0.0-beta](https://github.com/alibaba/havenask/tree/1.0.0-beta),
> [main-stable-0.4](https://github.com/alibaba/havenask/tree/main-stable-0.4)<br>
> 新老main分支差异较大，如果同步代码分支出现错误，请与当前main分支保持一致。

## 项目介绍

[![Leaderboard](https://img.shields.io/badge/HavenAsk-%E6%9F%A5%E7%9C%8B%E8%B4%A1%E7%8C%AE%E6%8E%92%E8%A1%8C%E6%A6%9C-orange)](https://opensource.alibaba.com/contribution_leaderboard/details?projectValue=havenask)

Havenask是阿里巴巴集团自研的搜索引擎，也是阿里巴巴内部广泛使用的大规模分布式检索系统，支持了包括淘宝、天猫、菜鸟、高德、饿了么、全球化在内整个阿里巴巴集团的搜索业务，为用户提供高性能、低成本、易用的搜索服务，同时具有灵活的定制和开发能力，支持算法快速迭代，帮助客户和开发者量身定做适合自身业务的智能搜索服务，助力业务增长。

此外，基于Havenask打造的行业AI搜索产品——[阿里云OpenSearch](https://www.aliyun.com/product/opensearch)，也将持续在阿里云上为企业级开发者提供全托管、免运维的一站式智能搜索服务，欢迎企业级开发者们试用。

支持与大语言模型结合，实现基于文档的问答系统，详情参考[llm](llm/README.zh-CN.md)

## 核心能力
Havenask 的核心能力与优势，有以下几点：
* <strong>极致的工程性能</strong>：支持千亿级数据实时检索，百万QPS查询，百万TPS写入，毫秒级查询延迟与秒级数据更新。
* <strong>C++的底层构建</strong>：对性能、内存、稳定性有更高保障。
* <strong>SQL查询支持</strong>：支持SQL语法便捷查询，查询体验更友好。
* <strong>丰富的插件机制</strong>：支持各类业务插件，拓展性强。
* <strong>支持图化开发</strong>：实现算法分钟级快速迭代，定制能力丰富，在新一代智能检索场景下的支持效果优秀。
* <strong>支持向量检索</strong>：可通过与插件配合实现多模态搜索，满足更多场景的搜索服务搭建需求。

## 相关文档
* Havenask官网: [https://havenask.net](https://havenask.net)
* 仓库内文档: [docs/havenask_docs/sql](docs/havenask_docs/sql)

## 开始使用
* 镜像介绍（镜像平台: amd64）
   * ha3_runtime：可直接运行的镜像，无需编译代码，包含了问天引擎的可执行文件。
   * ha3_dev：用于开发测试的镜像，里面包含了开发测试时需要的各种依赖库和头文件，如何编译问天引擎请参考[QuickStart](https://havenask.net/#/doc/sql/guide/quickstart)。
* 环境要求
   * 运行镜像：确保机器内存大于4G，cpu大于2核，磁盘大小大于20G。
   * 开发镜像：确保机器内存大于10G，cpu大于2核，磁盘大小大于50G。
   * 使用前确保设备已经安装和启动Docker服务。
   * 单机模式需要确保本机能免密ssh登录自己，详情参考[单机模式](https://havenask.net/#/doc/sql/petool/localmode)

## 启动服务

* 创建容器
其中CONTAINER_NAME为指定的容器名
```
wget https://github.com/alibaba/havenask/releases/download/v1.2.0/create_container.sh
docker pull registry.cn-hangzhou.aliyuncs.com/havenask/ha3_runtime:latest
./create_container.sh <CONTAINER_NAME> registry.cn-hangzhou.aliyuncs.com/havenask/ha3_runtime:latest
```

* 登陆容器
```
./<CONTAINER_NAME>/sshme
```

* 启动havenask服务
```
/ha3_install/hape start havenask
```
* 创建表
```
/ha3_install/hape create table -t in0 -s /ha3_install/example/cases/normal/in0_schema.json -p 1
```

* 写入数据
```
/ha3_install/sql_query.py --query "insert into in0 (createtime,hits,id,title,subject)values(1,2,4,'测试', '测试')"
```
* 查询数据
```
/ha3_install/sql_query.py --query "select * from in0"
```

## 联系我们
官方技术交流钉钉群：

![havenask_dingding](https://github.com/user-attachments/assets/c4590da7-af53-4757-b919-53be87f49338)
