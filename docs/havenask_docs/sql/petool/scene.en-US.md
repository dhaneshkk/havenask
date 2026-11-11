---
toc: content
order: 5
---

# Common Hape operations

## Manage multiple clusters with hape
* Every hape command accepts the optional `-c` parameter to specify the cluster configuration path.
* Clusters are isolated from each other by `domainZkRoot` in `global.conf` together with each cluster's `serviceName`, which lets one hape manage multiple clusters.
* Note that in the current version the admin, QRS and searcher ports of a havenask cluster are fixed. If you manage multiple clusters, give them different ports to avoid conflicts.

## Update the cluster templates
* `cluster_templates` in the cluster configuration holds the cluster templates. The clusters and tables you create get their actual configuration by rendering these templates.
* After you change a template, run the subcommand below. Templates are managed by the havenask admin and cannot be updated dynamically in the current version, so this command restarts the havenask admin (not the workers), which then reloads the latest cluster configuration.
```
## Update existing cluster configuration from the templates
hape update template
```
* The current version does not support adding new files to a template; you can only modify files that already exist in it, such as `searcher_hippo.json`.

## Update a table schema
* Versions before 1.1.0 cannot update an existing table dynamically, so delete the table and create it again:
```
hape delete table <options-and-arguments>
hape create table <options-and-arguments>
```
* From 1.1.0, the schema of a full table can be updated dynamically. A full build runs automatically and the index is switched over when it finishes:
```
hape update table-schema <options-and-arguments>
```

## Update table configuration
* If you only want template changes to apply to newly created tables, run:
```
## Update existing cluster configuration from the templates
hape update template
```
* To update the configuration of an existing table: the current version cannot update existing tables dynamically, so delete the table, update the templates, then create the table again. The database may not be ready immediately afterwards; use the `gs` command to check that it eventually becomes ready (see [Hape cluster status](./status.md)).
```
hape delete table <options-and-arguments>
hape update template
hape create table <options-and-arguments>
```

```
hape gs havenask
```

### Update the index load strategy and online index configuration
Update the online configuration of a table that already exists, such as real-time build memory or the index load strategy:
```
hape update load-strategy <options-and-arguments>
```

## Adjust cluster resources and parameters
Adjusting cluster resources and parameters means editing the corresponding `hippo.json` in the cluster templates.
* Before 1.1.0, restart the havenask or swift cluster afterwards:
```
hape restart havenask/swift
```
* From 1.1.0, `hippo.json` can be updated dynamically:
```
hape update hippo-config <options-and-arguments>
```
Use the `get` command to see the rendered default hippo configuration:

```
hape get default-hippo-config -r searcher
hape get default-hippo-config -r qrs
```


## Check cluster status
* Use `hape gs`; see [Hape cluster status](./status.md).



## Unhealthy nodes
* After a cluster has been running for a while, some nodes may become unhealthy.
* For problems a restart can fix, restart the node with `hape restart container` (see [Hape commands](./command.md)).
* For problems a restart cannot fix:
    * Stop the node with `hape stop container` (see [Hape commands](./command.md)).
    * Remove its IP from `global.conf` and add a new IP.
    * Run `hape update candidate` (see [Hape commands](./command.md)). After a while, hippo schedules the processes that belonged to the old machine onto the new one.
* Finish by checking with `hape gs` that the havenask cluster is READY.



## SQL warm-up
* The first queries after the engine starts are slow because the framework has to warm up query processing; later queries are much faster. To avoid this, configure SQL warm-up.
* Add the following to `cluster_templates/havenask/direct_table/biz_config/sql.json` in the hape templates:
```
"iquan_warmup_config": {
     "thread_number" : 2,  // number of warm-up threads; default 2, a larger value is recommended
     "warmup_file_path": "warmup_sql.txt" // file of warm-up SQL for your workload, placed next to sql.json
}
```
* `warmup_sql.txt` has the following format; list the queries your workload needs warmed up:
```
{
    "sqls":[
        "SELECT i1, min(i2) FROM t1 GROUP BY i1"
    ]
}
```

## Metrics
* To enable monitoring for a havenask cluster, change the following environment variable from `false` to `true` in `hape/hape_conf/default/cluster_templates/havenask/hippo/qrs_hippo.json` and `hape/hape_conf/default/cluster_templates/havenask/hippo/searcher_hippo.json`:

```
{
    "key": "--env",
    "value": "kmonitorEnableLogFileSink=true"
},
```

## Change the analyzer
* Analyzer definitions for direct-write tables:
    * `cluster_templates/havenask/direct_table/analyzer.json`
    * `cluster_templates/havenask/direct_table/biz_config/analyzer.json`
* Analyzer definitions for full tables:
    * `cluster_templates/havenask/offline_table/analyzer.json`
* Use the jieba analyzer already defined in the templates as a reference. After editing the analyzer definition files, run:
```
hape update template
```

## High availability
* See the `count` and `minHealthCapacity` parameters under the havenask process scheduling configuration in [hape-config](./config/hape-config.md).
* `count` is the number of replicas of each data partition.
* `minHealthCapacity` is the fraction of replicas that stays available during rolling changes.
