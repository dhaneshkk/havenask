---
toc: content
order: 0
---

# Hape single-machine mode

* Single-machine mode runs all the containers of a havenask cluster on one machine. It is mainly for trying things out.
* If anything below fails, see [Hape FAQ and troubleshooting](./problem.md).


### 1. Prepare the environment and configuration

#### Prepare the environment
* The latest image is `registry.cn-hangzhou.aliyuncs.com/havenask/ha3_runtime:latest`. Each version has its own image; see the [release pages](../guide/releasepages) for image versions. Make sure you have already pulled the image for your version with docker.
* Make sure the machine can SSH to itself without a password. To set that up:
```
ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
ssh-copy-id -i ~/.ssh/id_rsa `hostname -i`
```

#### Configuration
* By default, hape uses `/ha3_install/hape_conf/default` as the cluster configuration; no changes are needed.
* For what each setting means, see [Hape configuration](./config/hape-config.md).


### 2. Create the havenask cluster

* Create the hape container and enter it:
```
./docker/havenask/create_container.sh <container_name> <image>
./<container_name>/sshme
```

* (Optional) Check that the hape environment has no obvious problems:
```
hape validate
```

* Create the havenask cluster. The containers for all subsequent processes are started on this machine.
```
hape start havenask
```

* The cluster status is not ready yet at this point: a cluster only becomes ready after at least one table has been created.
```
hape gs havenask
```

### 3. Manage tables
* havenask has two kinds of tables, direct-write tables and full tables. Create either kind, or both.
* Create a direct-write table:
    * `-t`: table name
    * `-p`: number of partitions; must be 1 on a single machine
    * `-s`: schema path
```
hape create table -t in0 -p 1 -s /ha3_install/example/cases/normal/in0_schema.json

```
* (Optional; slow to start) Create a full table:
    * `-t`: table name
    * `-p`: number of partitions; must be 1 on a single machine
    * `-s`: schema path
    * `-f`: path to the full data, as a file or a directory
```
hape create table -t in1 -p 1 -s /ha3_install/example/cases/normal/in0_schema.json  -f /ha3_install/example/data/test.data
```
* A full table needs the build service, which starts several build tasks, so it usually takes 3–5 minutes to take effect. Check the build service status with the commands below; see [Hape cluster status](./status.md) for what the states mean.
```
hape gs bs

## Once every "full" process has finished and only "inc" processes remain, this shows the table as READY
hape gs table -t <table_name>
```

* To delete a table:
```
hape delete table -t <table-name>
```

### 4. Check the cluster status
* After creating tables, check whether the cluster is ready for reads and writes with the command below; see [Hape cluster status](./status.md) for what the states mean.
```
## The cluster is ready when clusterStatus under sqlClusterInfo is READY
hape gs havenask
```

### 5. Read and write data
* Write to a direct-write table:
```
/ha3_install/sql_query.py --query "insert into in0 (createtime,hits,id,title,subject)values(1,2,4,'test', 'test')"
```

* Query the table:
```
/ha3_install/sql_query.py --query "select * from in0"
```

* To see the values of text fields, join with the [summary index](../indexes/summary.md):
```
/ha3_install/sql_query.py --query "select in0_summary_.id, in0_summary_.title, in0_summary_.subject from in0 inner join in0_summary_ on in0.id=in0_summary_.id"
```



* Pushing real-time data to a full table goes through swift. The swift C++ or Java client is recommended; Python only has a test writer, which is not recommended for production. The test writer's parameters are:
    * `--zk`: ZooKeeper address of the swift service
    * `--topic`: swift topic name; by default usually the table name
    * `--count`: number of partitions of the swift topic; by default usually the number of table partitions
    * `--schema`: path to the table schema
    * `--file`: havenask data file to write
```
## Get the serviceZk address of swift; with the default configuration it is zfs://<localhost>:2181/havenask/havenask-swift-local
hape gs swift

## Write test messages
/ha3_install/swift_writer.py --zk <serviceZk> --topic in1 --count 1 --schema /ha3_install/example/cases/normal/in0_schema.json --file /ha3_install/example/data/rt.data
```

### 6. Clean up the cluster
```
## Clean up the havenask cluster: delete its containers and ZooKeeper data
hape delete havenask

## Clean up the swift cluster: delete its containers and ZooKeeper data
hape delete swift
```

### 7. More
* For more subcommands, see [Hape commands](./command.md).
* For more operations, see [Common Hape operations](./scene.md).
* For more single-machine examples, see [the hape examples README](https://github.com/alibaba/havenask/blob/main/aios/tools/hape/example/README.md).
