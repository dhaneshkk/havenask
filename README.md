English | [简体中文](README.zh-CN.md)

## Note
> Older versions:
> [1.2.0](https://github.com/alibaba/havenask/tree/1.2.0),
> [1.1.0](https://github.com/alibaba/havenask/tree/1.1.0),
> [1.0.0](https://github.com/alibaba/havenask/tree/1.0.0),
> [1.0.0-beta](https://github.com/alibaba/havenask/tree/1.0.0-beta),
> [main-stable-0.4](https://github.com/alibaba/havenask/tree/main-stable-0.4)<br>
> The current main branch differs significantly from the old main branch. If syncing your code branch produces errors, bring it in line with the current main branch.

## Introduction

[![Leaderboard](https://img.shields.io/badge/HavenAsk-Check%20Your%20Contribution-orange)](https://opensource.alibaba.com/contribution_leaderboard/details?projectValue=havenask)

Havenask is a search engine developed by Alibaba Group and a large-scale distributed retrieval system used widely inside Alibaba. It powers search for businesses across the group, including Taobao, Tmall, Cainiao, Amap, Ele.me and Alibaba's global services. It provides high-performance, low-cost, easy-to-use search, with flexible customization and development capabilities that support fast algorithm iteration, so customers and developers can build intelligent search services tailored to their business.

[Alibaba Cloud OpenSearch](https://www.aliyun.com/product/opensearch), an industry AI search product built on Havenask, offers enterprise developers a fully managed, maintenance-free, one-stop intelligent search service on Alibaba Cloud.

Havenask can be combined with large language models to build document-based question answering; see [llm](llm/README.md).

## Key features
* <strong>Top engineering performance</strong>: real-time search over hundreds of billions of records, millions of queries per second (QPS) and millions of writes per second (TPS), with millisecond query latency and data updates visible within seconds.
* <strong>Built in C++</strong>: stronger guarantees for performance, memory use and stability.
* <strong>SQL queries</strong>: query with familiar SQL syntax.
* <strong>Rich plugin mechanism</strong>: supports many kinds of business plugins, so the engine is highly extensible.
* <strong>Graph-based development</strong>: iterate on algorithms in minutes, with rich customization and strong results for next-generation intelligent retrieval.
* <strong>Vector search</strong>: combined with plugins, supports multimodal search for a wider range of search services.

## Documentation
* Havenask website: [https://havenask.net](https://havenask.net)
* Documentation in this repository: [docs/havenask_docs/sql](docs/havenask_docs/sql) (English pages end in `.en-US.md`)

## Get started
* Images (platform: amd64)
   * <strong>ha3_runtime</strong>: ready-to-run image containing the Havenask executables; no compilation needed.
   * <strong>ha3_dev</strong>: development image with the libraries and headers needed to build and test Havenask. To build Havenask, see [QuickStart](https://havenask.net/#/doc/sql/guide/quickstart).
* Requirements
   * Runtime image: more than 4 GB of memory, more than 2 CPU cores, more than 20 GB of disk.
   * Development image: more than 10 GB of memory, more than 2 CPU cores, more than 50 GB of disk.
   * Docker installed and running.
   * For single-machine mode, the machine must be able to SSH to itself without a password; see [Single-machine mode](https://havenask.net/#/doc/sql/petool/localmode).

## Start the service

* Create the container. `CONTAINER_NAME` is the container name.
```
wget https://github.com/alibaba/havenask/releases/download/v1.2.0/create_container.sh
docker pull registry.cn-hangzhou.aliyuncs.com/havenask/ha3_runtime:latest
./create_container.sh <CONTAINER_NAME> registry.cn-hangzhou.aliyuncs.com/havenask/ha3_runtime:latest
```

* Log in to the container
```
./<CONTAINER_NAME>/sshme
```

* Start the Havenask service
```
/ha3_install/hape start havenask
```
* Create a table
```
/ha3_install/hape create table -t in0 -s /ha3_install/example/cases/normal/in0_schema.json -p 1
```

* Write data
```
/ha3_install/sql_query.py --query "insert into in0 (createtime,hits,id,title,subject)values(1,2,4,'test', 'test')"
```
* Query data
```
/ha3_install/sql_query.py --query "select * from in0"
```

## Contact us
Havenask DingTalk group:

![havenask_dingding](https://github.com/user-attachments/assets/c4590da7-af53-4757-b919-53be87f49338)
