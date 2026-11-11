---
toc: content
order: 1
---

# Hape commands

* Run the following command for help with hape:

```
hape -h
```

* Subcommands have their own help, for example:

```
hape start -h

hape start havenask -h
```

## Subcommands

### start
* Purpose: start a cluster
* Arguments:
    * `havenask` starts the havenask cluster
    * `swift` starts the swift cluster
* Options:
    * `-c <config>` optional. The hape configuration to use. Defaults to `/ha3_install/hape_conf/default`.
    * `-v` optional. Enables hape debug-level logging.
* Notes
    * When the argument is `havenask`:
        * If the swift cluster does not exist, hape starts it automatically from the configuration.
        * If `domainZkRoot` is not set in `global.conf` of the chosen cluster configuration, hape automatically starts the default test ZooKeeper.
```
## Start the swift cluster
hape start swift

## Start the havenask cluster
hape start havenask

```


### stop
* Purpose: stop a cluster without clearing its ZooKeeper information
* Arguments:
    * `havenask`/`swift`/`container` stops the havenask cluster, the swift cluster, or a single container
* Options:
    * `-c <config>` optional. The hape configuration to use. Defaults to `/ha3_install/hape_conf/default`.
    * `-v` optional. Enables hape debug-level logging.
* Additional options:
    * When the argument is `container` (get these values from the `gs` subcommand):
        * `-i <ip>` IP address
        * `-n <name>` name of the container to stop on that machine
```
## Stop the swift cluster
hape stop swift

## Stop the havenask cluster
hape stop havenask

## Stop one container on a machine
hape stop container -i <ip> -n <container-name>

```


### restart
* Purpose: restart a cluster
* Arguments:
    * `havenask`/`swift`/`container` restarts the havenask cluster, the swift cluster, or a single container
    * `container` restarts one container; see [Common Hape operations](./scene.md) for usage
* Options:
    * `-c <config>` optional. The hape configuration to use. Defaults to `/ha3_install/hape_conf/default`.
    * `-v` optional. Enables hape debug-level logging.
* Additional options:
    * When the argument is `container`:
        * `-i <ip>` required. Machine IP.
        * `-n <name>` required. Container name.
```
## Restart the swift cluster
hape restart swift

## Restart the havenask cluster
hape restart havenask

## Restart one container on a machine
hape restart container -i <ip> -n <container-name>
```

### delete
* Purpose: delete a cluster or table and clear its ZooKeeper information
* Arguments:
    * `havenask`/`swift`/`table`/`all` selects what to delete
* Options:
    * `-c <config>` optional. The hape configuration to use. Defaults to `/ha3_install/hape_conf/default`.
    * `-v` optional. Enables hape debug-level logging.
* When the argument is `table`:
    * `-t <table>` required. The table to delete.
    * `--keeptopic` optional. Keep the table's swift topic when deleting it.

```
## Delete the swift cluster
hape delete swift

## Delete the havenask cluster
hape delete havenask

## Delete a havenask table
hape delete table -t <table>

## Delete havenask, its tables and swift in one go
hape delete all

```

### create
* Purpose: create a table
* Arguments:
    * `table` creates a table
* Options:
    * `-c <config>` optional. The hape configuration to use. Defaults to `/ha3_install/hape_conf/default`.
    * `-v` optional. Enables hape debug-level logging.
    * `-t <table>` required. Table name.
    * `-p <partition-count>` required. Number of partitions; must be 1 on a single machine. In multi-machine mode, do not use more partitions than there are searcher machines available for scheduling, or ports will conflict. Also in multi-machine mode, if there are N tables and the largest has M partitions, every table must have either 1 or M partitions.
    * `-s <schema>` required. Path to the schema.
    * `-f <file>` optional. Path to the full data, as a file or a directory. If given, a full table is created; otherwise a direct-write table is created. In multi-machine mode this must be an HDFS path.
* Notes:
    * A swift topic is created automatically with the table. You can also create a topic with the same name as the table in advance using the swift tools; table creation then reuses it.
```
## Direct-write table
hape create table -t in0 -p 1 -s /ha3_install/example/cases/normal/in0_schema.json

## Full table
hape create table -t in1 -p 1 -s /ha3_install/example/cases/normal/in0_schema.json  -f /ha3_install/example/cases/normal/test.data

```

### gs
* Purpose: get status; see [Hape cluster status](./status.md) for what it means
* Arguments
    * `swift`/`table`/`havenask`/`bs` gets the status of swift, tables, havenask or the build service
* Options
    * `-c <config>` optional. The hape configuration to use. Defaults to `/ha3_install/hape_conf/default`.
    * `-v` optional. Enables hape debug-level logging.

* Additional options
    * When the argument is `table`:
        * `-t <table-name>` optional. Show only that table's status.

```
## swift status
hape gs swift

## havenask cluster status
hape gs havenask

## Table status
hape gs table
hape gs table -t in0

## Build service status
hape gs bs

```


### validate
* Purpose: basic checks on the cluster, such as connectivity and whether containers can be scheduled
* Options
    * `-c <config>` optional. The hape configuration to use. Defaults to `/ha3_install/hape_conf/default`.
    * `-v` optional. Enables hape debug-level logging.

```
hape validate
```


### update
* Purpose: update parts of the hape configuration; see [Common Hape operations](./scene.md) for details
* Arguments:
    * `candidate` updates the list of IPs available for scheduling, from `global.conf`
    * `template` restarts the havenask admin so it loads the latest templates
    * `hippo-config` updates cluster startup parameters, binaries and so on
    * `load-strategy` updates the index load strategy and online index configuration
    * `table-schema` updates a table's schema, then runs a full build and switches over automatically

#### Update the machines available for scheduling
```
## Update the list of machine IPs available for scheduling
hape update candidate
```


#### Update table templates
```
## Restart the havenask admin to load the latest templates
hape update template
```

#### Update the schema of a full table
```
hape update table-schema -t {table_name} -p {part} -s {schema} -f {data}
```
- `{table_name}`: table whose schema is updated
- `{part}`: number of partitions of the full table
- `{schema}`: path to the new schema file
- `{data}`: full table data

Example:
```
hape update table-schema -t in0 -p 1 -s /path/to/schema -f /path/to/data
```

#### Update the load strategy
```
hape update load-strategy -t {table_name} -s '{online_index_config}'
```
- `{table_name}`: table whose load strategy is updated
- `{online_index_config}`: a JSON string in the format of `online_index_config` in the [cluster configuration](./config/clusterconfig.md)

Example:
```
hape update load-strategy -t in0 -s '{"build_config": {"build_total_memory": 3456}, "load_config": [{"load_strategy_param": {"lock": true}, "load_strategy": "mmap", "name": "all_lock_value", "file_patterns": [".*"]}], "max_realtime_memory_use": 6543}'
```

#### Update binaries, startup parameters and more
```
hape update hippo-config -p {hippo_config_file_path} -r {role_type}
```
- `{hippo_config_file_path}`: the hippo config file to apply. It describes the process: binary (currently the image), startup parameters, `minHealthCapacity` and so on.
- `{role_type}`: role to update: `searcher` or `qrs`

Example:
```
hape update hippo-config -p /path/to/hippo_config -r searcher
```


### get
* Purpose: get configuration content (currently only the default hippo configuration of searcher or QRS)
* Arguments
    * `default-hippo-config`

```
## Default hippo configuration for QRS
hape get default-hippo-config -r qrs

## Default hippo configuration for searchers
hape get default-hippo-config -r searcher
```
