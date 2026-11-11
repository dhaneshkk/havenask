---
toc: content
order: 2
---
# Hape multi-machine mode

* Multi-machine mode schedules and runs a havenask cluster across several physical machines.
* If anything below fails, see [Hape FAQ and troubleshooting](./problem.md).


### 1. Prepare the environment and configuration
#### Prepare the environment

* Prepare several physical machines.
* The latest image is `registry.cn-hangzhou.aliyuncs.com/havenask/ha3_runtime:latest`. Each version has its own image; see the [release pages](../guide/releasepages) for image versions. Make sure every physical machine has already pulled the image for your version with docker.
* Every machine must have the same user that runs hape, and that user must have full permissions on its home directory. Using root is not recommended.
* Passwordless SSH must work between the machines, and each machine must be able to SSH to itself without a password. If it doesn't:
  * Check whether `.ssh/id_rsa.pub` exists in the user's home directory on each machine. If not, generate it with `ssh-keygen`.
  * Copy `id_rsa.pub` to the other machines with `ssh-copy-id`.

#### Edit the configuration
* Edit `/ha3_install/hape_conf/remote`. For what each setting means, see [Hape configuration](./config/hape-config.md).
##### HDFS
* In multi-machine mode, machines in the havenask cluster share configuration, indexes and other data, so you need an HDFS file system. The current havenask engine requires Java 8; download any Hadoop version that works with Java 8 and start HDFS. Then:
  * Create the data directories:
    * Create two directories in HDFS, `hdfs://xxx/havenask` and `hdfs://xxx/swift`, for havenask and swift data respectively.
    * Grant permissions on both directories with `hadoop fs -chmod 777`.
  * Set the variables:
    * `javaHome` in `global.conf`: the Java path. Containers must be able to reach it, so the Java directory must be somewhere under `/home/<user>`, which is mounted into the containers. If it isn't, use a symbolic link.
    * `hadoopHome` in `global.conf`: the Hadoop path. Containers must be able to reach it, so the Hadoop directory must be somewhere under `/home/<user>`, which is mounted into the containers. If it isn't, use a symbolic link.
    * `dataStoreRoot` in `global.conf`: the `hdfs://xxx/havenask` directory above.
    * `data_root_path` in `cluster_templates/swift/config/swift.conf`: the `hdfs://xxx/swift` directory above.
* If HDFS gives you trouble in multi-machine mode, see [HDFS does not work in multi-machine mode](./problem.md#hdfs-does-not-work-in-multi-machine-mode).

##### Machines available for scheduling

* You must edit `global.conf`:
    * swift:
        * machines available for scheduling: `adminIpList` and `workerIpList`
    * havenask:
        * machines available for scheduling: `adminIpList`, `qrsIpList` and `searcherIpList`
        * There must be at least as many searcher machines as the number of partitions of the tables you create later.
        * In the current version, QRS and searchers cannot share machines, but the admin can share a machine with QRS or a searcher.
    * bs:
        * machines available for scheduling: `adminIpList` and `workerIpList`


### 2. Create the havenask cluster

* Create the hape container and enter it:
```
./docker/havenask/create_container.sh <container_name> <image>
./<container_name>/sshme
```

* Check that the hape environment has no obvious problems. Multi-machine mode does not use the default configuration, so every command from here on must specify the distributed cluster configuration path `/ha3_install/hape_conf/remote`:
```
hape validate -c /ha3_install/hape_conf/remote
``` 

* Create the havenask cluster:
```
hape start havenask -c /ha3_install/hape_conf/remote
```


### 3. Manage tables
* havenask has two kinds of tables, direct-write tables and full tables. Create either kind, or both.
* Create a direct-write table:
    * `-t`: table name
    * `-p`: number of partitions. In multi-machine mode, if there are N tables and the largest has M partitions, every table must have either 1 or M partitions.
    * `-s`: schema path
```
hape create table -t in0 -p 2 -s /ha3_install/example/cases/normal/in0_schema.json -c /ha3_install/hape_conf/remote

```
* (Optional; slow to start) Create a full table:
    * `-t`: table name
    * `-p`: number of partitions. In multi-machine mode, if there are N tables and the largest has M partitions, every table must have either 1 or M partitions.
    * `-s`: schema path
    * `-f`: path to the full data, as a file or a directory. In distributed mode you must upload the data first and pass an HDFS path.
```
## First upload /ha3_install/example/data/test.data with the HDFS tools
## 
hape create table -t in1 -p 2 -s /ha3_install/example/cases/normal/in0_schema.json  -f hdfs://xxxx/test.data -c /ha3_install/hape_conf/remote
```
* A full table needs the build service, which starts several build tasks, so it usually takes 3–5 minutes to take effect. Check the build service status with the commands below; see [Hape cluster status](./status.md) for what the states mean.
```
hape gs bs -c /ha3_install/hape_conf/remote

## Once every "full" process has finished and only "inc" processes remain, this shows the table as READY
hape gs table -t <table_name> -c /ha3_install/hape_conf/remote
```

* To delete a table:
```
hape delete table -t <table-name> -c /ha3_install/hape_conf/remote
```

### 4. Check the cluster status
* After creating tables, check whether the cluster is ready for reads and writes with the command below; see [Hape cluster status](./status.md) for what the states mean.
```
## The cluster is ready when clusterStatus under sqlClusterInfo is READY
hape gs havenask -c /ha3_install/hape_conf/remote
```


### 5. Read and write data

* Write to a direct-write table:
```
## QRS may run on a remote machine, so first get its address with hape gs havenask
/ha3_install/sql_query.py  --address  http://<qrs-ip>:45800 --query "insert into in0 (createtime,hits,id,title,subject)values(1,2,4,'test', 'test')"
```

* Query the table:
```
/ha3_install/sql_query.py  --address  http://<qrs-ip>:45800 --query "select * from in0" 
```

* To see the values of text fields, join with the [summary index](../indexes/summary.md):
```
/ha3_install/sql_query.py --address  http://<qrs-ip>:45800 --query "select in0_summary_.id, in0_summary_.title, in0_summary_.subject from in0 inner join in0_summary_ on in0.id=in0_summary_.id"
```


* Pushing real-time data to a full table goes through swift. The swift C++ or Java client is recommended; Python only has a test writer, which is not recommended for production. The test writer's parameters are:
    * `--zk`: ZooKeeper address of the swift service
    * `--topic`: swift topic name; by default usually the table name
    * `--count`: number of partitions of the swift topic; by default usually the number of table partitions
    * `--schema`: path to the table schema
    * `--file`: havenask data file to write
```
## Get the serviceZk address of the swift service
hape gs swift

## Write test messages
/ha3_install/swift_writer.py --zk <serviceZk> --topic in1 --count 2 --schema /ha3_install/example/cases/normal/in0_schema.json --file /ha3_install/example/data/rt.data 
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
* For more single-machine examples, see `aios/tools/hape/example/README.md`.
