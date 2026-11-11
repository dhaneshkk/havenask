---
toc: content
order: 8
---

# Hape FAQ and troubleshooting

## Troubleshooting hape command errors
### 1. Hape commands that help with debugging
* `hape validate` runs basic checks.
* Add `-v` to any hape command to see exactly what hape does, so you can tell which step fails.
* Example: if the `-v` output shows that creating a container failed, copy the container-creation command from the log and run it yourself to find the problem.

### 2. Process startup errors
* If `hape start` has trouble starting processes, usually either creating the admin container failed or the admin process failed to start.
* If the error is about the admin failing to create a container, use `-v` to find which command failed.
* If the error says the admin is not ready, the admin process failed to start (the container is fine). Use `hape gs` to find which machine the admin runs on and check the most recent ERROR lines in its logs; see [Engine logs](#engine-logs) below.


### 3. Table operation errors
* If a hape table command fails, the table configuration may be wrong. Use `hape gs havenask` to find which machines QRS and the searchers run on and check the most recent ERROR lines in their logs; see [Engine logs](#engine-logs) below.


## Engine logs
* Errors from the engine admin and workers are diagnosed from the engine logs:
    1. Use `hape gs` to find the machine a process runs on.
    2. By default, the havenask cluster creates every process's working directory under `/home/<user>`. On a machine, run `ls ~ | grep havenask | grep <serviceName>`, where `serviceName` is the service name set in `global.conf` of the cluster configuration. The appmaster is the admin.
    3. Logs:
          * Basic logs for every process:
              * Startup logs: `<workdir>/stdout.log` and `<workdir>/stdin.log`
          * Main havenask admin logs:
              * Cluster process scheduling: `<workdir>/hippo.log`
              * Cluster targets: `<workdir>/suez.log`
          * Main havenask worker log:
              * SQL engine: `<workdir>/ha_sql/logs/sql.log`
          * Main swift admin logs:
              * Cluster process scheduling: `<workdir>/logs/hippo.log`
              * Cluster targets: `<workdir>/logs/swift/swift.log`
          * Main swift broker log:
              * Broker: `<workdir>/logs/swift/swift.log`

## Working with engine containers
* Log in to a container:

```
find <workdir> -name sshme
```

```
bash <path-to>/sshme
```

* Restart a process manually:
  * Enter the container, then find and kill the process with `ps -aux`.
  * Run the process startup script:
```
find <workdir> -name process_starter.sh
```

```
bash <path-to>/process_starter.sh & 
```



## Other common questions

### How hape works
* Everything hape does goes through the havenask, swift and bs admins.
* The admins adjust the workers based on the schedulable machine list and cluster targets that hape gives them. hape does not control workers directly.


### Processes fail to start
* Container creation fails and `-v` shows permission problems:
  * Do not use the root account, and make sure the current account has full permissions under `/home/<user>`.
* Container creation fails and `docker ps --all` shows the container exited:
    * Run `sudo chmod 666 /var/run/docker.sock` on that machine.

* Creating a swift topic times out:
    * Usually caused by wrong `hadoopHome` and `javaHome` settings in multi-machine mode.
    * Use `hape gs swift` to check whether the brokers started.
    * Check the admin and broker logs for errors.

* QRS does not reach its target replica count, or `hape gs havenask` shows some processes unhealthy:
    * Check the logs to see whether a port is already in use.
    * Restart the node with `hape restart container`.

### Vector indexes
* A vector index has no effect and queries return nothing after inserting data:
    * Use the vector example's templates in `/ha3_install/example/cases/vector/vector_conf` as a reference; its `data_tables` differ from the normal configuration.

### HDFS does not work in multi-machine mode
* In multi-machine mode, every machine must be able to reach the configured address through your Hadoop path.
* To verify the configuration:
  * Enter a container and check that the following command succeeds. `JAVA_HOME` and `HADOOP_HOME` are your configured Java and Hadoop paths, and `DATA_STORE_ROOT` is your havenask data directory for multi-machine mode.

```
JAVA_HOME=<JAVA_HOME> HADOOP_HOME=<HADOOP_HOME> /ha3_install/usr/local/bin/fs_util ls <DATA_STORE_ROOT>
```

* If it reports a permission error, grant 777 permissions on the directory with the HDFS tools.


### Find out where a process runs
* Run `hape gs havenask` to see which machine each process runs on.
