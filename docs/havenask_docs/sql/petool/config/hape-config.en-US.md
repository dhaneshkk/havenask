---
toc: content
order: 0
---
# Hape configuration

## Overview
* Hape's configuration lives in `hape_conf`. If you do not specify one, `hape_conf/default` is used.
<Tree>
  <ul> 
    <li>default
      <ul>
        <ul>
        <li>global.conf (global Hape configuration)</li> 
        <li>cluster_templates
            <ul>
            <li>havenask (havenask engine process configuration)
                <ul>
                    <li>...</li>
                </ul>
            </li>
            <li>swift (havenask message queue process configuration)
                <ul><li>...</li></ul>
            </li>
            </ul>
        </li> 
        </ul>
    </li>
    </ul>
  </ul>
</Tree>

* You can create your own Hape configurations under `hape_conf` to manage multiple clusters. They must use the same layout as `hape_conf/default`.

## Variable rendering
* Much of the havenask configuration is generated dynamically, so Hape configuration files support variable rendering.
* Variables use the form `${xxx}`. The built-in variables are:
    * `user`: user name
    * `userHome`: user's home directory
    * `hapeRoot`: hape root directory
    * `localHost`: IP address of the local machine
    * `defaultImage`: default image
    * Every variable in `global.conf` is also available. For example, `${common.binaryPath}` renders the `binaryPath` variable from the `common` section of `global.conf`.

## global.conf (global configuration)
### global.conf.common
* Purpose: global parameters
* Parameters
    * `domainZkRoot`: root ZooKeeper path for one data center. `domainZkRoot/serviceName` becomes the root ZooKeeper path of each kind of cluster. If `domainZkRoot` is not set, Hape starts a test ZooKeeper for you.
    * `binaryPath`: where container processes find the havenask binary package; usually `/ha3_install`.
    * `dataStoreRoot`: location of the indexes, configuration and metadata files the havenask cluster produces while running. Relative paths are relative to `hapeRoot`. In multi-machine mode this must be an HDFS path.
    * `hadoopHome`: Hadoop path. It must be under `/home/<user>` (a symbolic link is fine), and Hadoop must exist at that path on every machine. Defaults to `/usr/local/hadoop/hadoop`, the default path inside the container.
    * `javaHome`: Java path. It must be under `/home/<user>` (a symbolic link is fine), Java must exist at that path on every machine, and it must match `hadoopHome`. Defaults to `/opt/taobao/java`, the default path inside the container.
    * `processorMode`: by default, single-machine mode starts a cluster of multiple containers on one machine. Set this to `proc` to start a single container running multiple processes instead, which is more convenient for debugging and development.


### global.conf.swift
* Purpose: swift cluster parameters
* Parameters
    * `swiftZkRoot`: swift ZooKeeper path. If not set, Hape starts a test swift for you.
    * `serviceName`: swift service name
    * `image`: image address
    * `adminCpu`: admin CPU quota; divide by 100 for the number of cores
    * `adminMem`: admin memory, in MB
    * `adminIpList`: admin machine IPs, separated by semicolons. Defaults to the local IP. Multiple admins elect a leader.
    * `workerIpList`: worker machine IPs, separated by semicolons. Defaults to the local IP.
    * `extraArgs`: extra startup arguments for the admin, separated by semicolons
    * `extraEnvs`: extra environment variables for the admin, separated by semicolons

### global.conf.havenask
* Purpose: online cluster parameters
* Parameters
    * `serviceName`: havenask service name
    * `image`: image address
    * `adminCpu`: admin CPU quota; divide by 100 for the number of cores
    * `adminMem`: admin memory, in MB
    * `adminIpList`: admin machine IP. Defaults to the local IP.
    * `qrsIpList`: QRS machine IPs, separated by semicolons. Defaults to the local IP. Multiple admins elect a leader.
    * `searcherIpList`: searcher machine IPs, separated by semicolons. Defaults to the local IP.
    * `adminHttpPort`: HTTP port of the havenask admin. Defaults to 45800.
    * `extraArgs`: extra startup arguments for the admin, separated by semicolons
    * `extraEnvs`: extra environment variables for the admin, separated by semicolons

### global.conf.bs
* Purpose: parameters for the cluster that builds full tables
* Parameters
    * `serviceName`: build service name
    * `image`: image address
    * `adminCpu`: admin CPU quota; divide by 100 for the number of cores
    * `adminMem`: admin memory, in MB
    * `adminIpList`: admin machine IPs, separated by semicolons. Defaults to the local IP. Multiple admins elect a leader.
    * `workerIpList`: worker machine IPs, separated by semicolons. Defaults to the local IP.
    * `extraArgs`: extra startup arguments for the admin, separated by semicolons
    * `extraEnvs`: extra environment variables for the admin, separated by semicolons



## havenask process scheduling configuration
* `hippo/qrs_hippo.json`
    * Purpose: process template used to start havenask QRS.
    * Parameters
        * `count`: number of replicas
        * `minHealthCapacity`: minimum availability. The admin keeps at least `minHealthCapacity/100 * count` replicas available.
        * `resources`: container resources for the process
        * `args`: startup arguments
        * `envs`: environment variables
* `hippo/searcher_hippo.json`
    * Purpose: process template used to start havenask searchers.
    * Parameters
        * `count`: number of replicas
        * `minHealthCapacity`: minimum availability. The admin keeps at least `minHealthCapacity/100 * count` replicas available.
        * `resources`: container resources for the process
        * `args`: startup arguments
        * `envs`: environment variables

## swift process scheduling configuration
* `config/swift_hippo.json`
    * Purpose: process template used to start swift brokers.
    * Parameters
        * `count`: number of replicas
        * `role_resource`: container resources for the process
        * `args`: startup arguments
        * `envs`: environment variables
* `swift.conf`
     * Purpose: swift cluster parameters
     * Parameters:
       * `data_root_path`: path where swift data is stored
