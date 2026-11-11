---
toc: content
order: 1
---

# Cluster configuration

A cluster configuration contains both the online (havenask) configuration and the offline (build_service) configuration.

The offline part configures the builder and merger. The cluster settings related to the build_service builder and merger are:
- `build_option_config`: index sorting.
- `online_index_config`: how indexes are loaded online.
- `offline_index_config`: build settings and the default merge settings, including periodic and full merge strategies and truncation.
- `swift_config`: the swift topics for processed documents and the builder's swift reader.
- `cluster_config`: cluster settings.
- `realtime`: `true` enables real-time updates.

A complete example cluster configuration file, `in0_cluster.json`:
```
{
    "build_option_config" : {
        "async_build" : true,
        "async_queue_size" : 1000,
        "document_filter" : true,
        "max_recover_time" : 30,
        "sort_build" : true,
        "sort_descriptions" : [
            {
                "sort_field" : "hits",
                "sort_pattern" : "asc"
            }
        ],
        "sort_queue_mem" : 4096,
        "sort_queue_size" : 10000000
    },
    "online_index_config": {
		"online_keep_version_count": 3,
		"build_config": {
			"build_total_memory": 4096
		},
		"max_realtime_memory_use": 10240,
		"load_config": [
			{
				"warmup_strategy": "sequential",
				"file_patterns": [
					"_INDEX_"
				],
				"load_strategy": "mmap",
				"name": "_INDEX_",
				"load_strategy_param": {
					"lock": false
				}
			},
			{
				"warmup_strategy": "none",
				"file_patterns": [
					"_SUMMARY_"
				],
				"load_strategy": "mmap",
				"name": "_SUMMARY_",
				"load_strategy_param": {
					"lock": false
				}
			},
			{
				"warmup_strategy": "sequential",
				"file_patterns": [
					"_ATTRIBUTE_"
				],
				"load_strategy": "cache",
				"name": "_ATTRIBUTE_",
				"load_strategy_param":{
                    "global_cache" : false,
                    "direct_io" : false
                }
			}
		]
	},
    "offline_index_config" : {
        "build_config" : {
            "build_total_memory" : 5120,
            "keep_version_count" : 40
        },
        "merge_config" :   
        {
            "merge_thread_count" : 3,
            "merge_strategy": "optimize",
            "merge_strategy_param": "",
            "document_reclaim_param" : "indexname=term1;indexname=term2",
            "uniq_pack_attribute_merge_buffer_size": 100,
            "truncate_strategy" : {...}
                
        },
        "customized_merge_config" :
        {
            "full":{
                "merge_config":{
                    "keep_version_count":40,
                    "merge_strategy":"optimize",
                    "merge_strategy_param":"after-merge-max-segment-count=20",
                    "merge_thread_count":4
                }
            },
            "inc"  :
            {
                "merge_config" : {
                    "merge_thread_count" : 5,
                    "merge_strategy": "optimize",
                    "merge_strategy_param": "",
                    "truncate_strategy" : {...}
                            
                },
                "period" : "period=1800",
                "merge_parallel_num" : 4,
                "need_wait_alter_field" : true
            },
            "merge-inc"  : {...}
               
        }
    },
    "cluster_config" : {
        "builder_rule_config" : {
            "batch_mode" : false,
            "build_parallel_num" : 1,
            "inc_build_parallel_num" : 1,
            "merge_parallel_num" : 1,
            "partition_count" : 1
        },
        "cluster_name" : "in0",
        "hash_mode" : {
            "hash_field" : "id",
            "hash_function" : "HASH"
        },
        "table_name" : "in0"
    },
    "swift_config" : {
        "topic_full": {
            "partition_count" : 10,
            "partition_min_buffer_size" : 10,
            "partition_max_buffer_size" : 1000,
            "partition_limit" : 10,
            "partition_file_buffer_size" : 100,
            "partition_resource" : 100,
            "obsolete_file_interval" : 3600,
            "reserved_file_count" : 10,
            "delete_topic_data" : true,
            "topic_mode" : "normal"
        },
        "topic_inc": {
            "partition_count" : 10,
            "partition_min_buffer_size" : 10,
            "partition_max_buffer_size" : 1000,
            "partition_limit" : 10,
            "partition_file_buffer_size" : 100,
            "partition_resource" : 100,
            "obsolete_file_interval" : 3600,
            "reserved_file_count" : 10,
            "delete_topic_data" : true,
            "topic_mode" : "normal"
        },        
        "reader_config" : "oneRequestReadCount=100;readBufferSize=10240;compress=true",
        "writer_config" : "functionChain=hashId2partId;mode=async|safe",
        "swift_client_config":"useFollowerAdmin=false;maxWriteBufferSizeMb=123;bufferBlockizeKb=124;mergeMessageThreadNum=22;tempWriteBufferPercent=0.23;refreshTime=122",
    },
    "direct_write" : true,  # enable direct-write mode
    "wal_config": { # WAL settings for direct-write mode
        "strategy": "realtime_swift",
        "sink": {
            "src": "swift",
            "type": "swift",
            "swift_root": "zfs://1.2.3.4:2181/xxx",
            "topic_name": "in0",
            "writer_config": "needTimestamp=true;functionChain=hashId2partId;compressThresholdInBytes=1024;mode=async|safe;maxBufferSize=2147483648;maxKeepInBufferTime=10000"
        },
        "timeout_ms": 10000
    },
    "realtime_info": {
        "need_field_filter": "true",
        "topic_name": "in0",
        "writer_config": "functionChain=hashId2partId;maxKeepInBufferTime=10000",
        "realtime_mode": "realtime_service_rawdoc_rt_build_mode",
        "src_signature": "1",
        "reader_config": "retryGetMsgInterval=50000;partitionStatusRefreshInterval=10000",
        "type": "swift",
        "swift_root": "zfs://1.2.3.4:2181/xxx"
    }  
}
```

### build_option_config
- `sort_build`: whether the index is sorted. Defaults to `false`.
- `sort_descriptions`: how the index is sorted. An array whose elements each contain a sort field (`sort_field`) and a sort order (`sort_pattern`). Multi-level sorting is supported: documents with equal values in the first field are ordered by the second, and so on.
- `sort_field`: a field from the schema configuration. Only numeric types such as INT, HASH, DOUBLE and FLOAT are allowed, and sort fields cannot be updated (update messages have no effect on them).
- `sort_pattern`: sort order, either ascending (`asc`) or descending (`desc`). Defaults to `desc`.
- `sort_queue_size`: size of each segment produced during the build. Documents accumulate in memory until this count is reached, then they are sorted and indexed. Defaults to `uint32_t::max()`.
- `sort_queue_mem`: in MB. Defaults to 60% of `build_total_memory`. The sort queue size is the smaller of `sort_queue_mem` and `sort_queue_size`.
- `document_filter`: whether documents may be filtered. Disabling it means the incremental and real-time streams carry the same documents, which improves HA3 reopen performance. Defaults to `true`.
- `async_build`: whether ProcessedDoc deserialization and building run asynchronously, each on its own thread. Defaults to `false`.
- `async_queue_size`: size of the intermediate queue for asynchronous builds. Defaults to 1000.
- `max_recover_time`: in seconds. The maximum time spent catching up on real-time messages after loading the full index.
- `recover_delay_tolerance_ms`: in milliseconds. While catching up on real-time messages after loading the full index, the engine is considered caught up once the gap between swift's latest locator and the engine's latest locator is below this value. Defaults to 1000 ms.
- `build_qps_limit`: in QPS. Rate limit for real-time builds.

### online_index_config
`online_index_config` controls how indexes are loaded online.
* `max_realtime_memory_use`: maximum memory for real-time data, in MB. This includes the segment being built, the operation queue, and real-time segments already dumped to memory. Defaults to 8 × 1024 (8 GB). It must be larger than `online_index_config.build_config.build_total_memory`.
* `build_config`: same as `offline_index_config.build_config`.
* `online_keep_version_count`: number of incremental index versions the online service keeps. When there are more, the oldest incremental indexes are deleted until the count is no larger than this value. Defaults to 10.
* `load_config`
  * `name`: optional. Used to name metrics when the block cache is not global. If not set, an ID is assigned in order.
  * `file_patterns`: regular expressions matching index files. Defaults to matching everything (`".*"`).
    * Built-in macros: `_ATTRIBUTE_`, `_INDEX_`, `_SUMMARY_`, defined as:
      * `_ATTRIBUTE_` = `"^segment_[0-9]+(_level_[0-9]+)?(/sub_segment)?/attribute/"`
      * `_INDEX_` = `"^segment_[0-9]+(_level_[0-9]+)?(/sub_segment)?/index/"`
      * `_SUMMARY_` = `"^segment_[0-9]+(_level_[0-9]+)?(/sub_segment)?/summary/"`
    * Matching: when an index file is opened, the patterns are tried in order and the first match decides how it is loaded. Files that match nothing are loaded with mmap, without locking.
  * `load_strategy`: how the index is loaded: `mmap` or `cache`. Defaults to `mmap`.
  * `load_strategy_param`: parameters for the chosen strategy.
  * `mmap`
    * `lock`: if `true`, the whole file is loaded into memory, locked so the system cannot swap it out, and warmed up. Defaults to `false`.
  * `cache`:
      * `global_cache`: whether to use the global BlockCache. Defaults to `false`.
      * For the global cache, `cache_size` is currently set through the `RS_BLOCK_CACHE` environment variable, for example `RS_BLOCK_CACHE=cache_size=1`.
      * `direct_io`: whether to read files with direct I/O. Defaults to `false`.
      * `cache_size`: total BlockCache size in MB when the cache is not global. Defaults to 1 MB.
      * `block_size`: block size in bytes. Defaults to 4096.
      * `cache_decompress_file`: if `true`, cache decompressed data; if `false`, cache compressed data. Defaults to `false`.
  * `warmup_strategy`: warm-up strategy; currently applies only to the mmap load strategy.
    * `lifecycle`: uses the lifecycle tag the updater writes to each segment; used together with the updater (see the offline build documentation).
    * `none`: no warm-up (default).
    * `sequential`: warm up by reading sequentially.



### offline_index_config
`offline_index_config` has three parts: `build_config`, `merge_config` and `customized_merge_config`.

- `build_config`: offline build settings.
    - `build_total_memory`: total memory used to build the index, in MB. Defaults to 6 GB. Can also be set with the `BUILD_TOTAL_MEM` environment variable. Precedence: user configuration > environment variable > built-in default.
    - `max_doc_count`: when the number of documents being built exceeds this limit, a dump is triggered. Defaults to `max_uint32`.
    - `keep_version_count`: number of versions kept after an index build. Applies to offline versions from incremental builds and local real-time versions from real-time builds; extra versions are deleted. Defaults to 2.
    - `enable_package_file`: whether to enable package files. If enabled, each index segment is packed into a single package file, which reduces load on HDFS.
    - `hash_map_init_size`: initial size of the hash map used when building inverted indexes.
    - `dump_thread_count`: number of threads used to dump the index.
    - `speedup_primary_key_reader`: whether to speed up primary key reads.
- `merge_config`: default merge settings.
    - `merge_thread_count`: number of parallel threads used for merging.
    - `merge_strategy`: index merge strategy.
    - `merge_strategy_param`: parameters for the merge strategy; see the description of merge strategies and their parameters.
    - `uniq_pack_attribute_merge_buffer_size`: only takes effect when the schema has a pack attribute with uniq compression. Controls the buffer size the pack attribute uses during merging. Defaults to 64 MB.
    - `document_reclaim_param`: conditions for reclaiming documents during a merge. Multiple conditions are ORed. Reclaiming applies to all segments, not only the ones being merged.
    - `truncate_strategy`: truncation strategy.
- `customized_merge_config`: user-defined merge settings. Lets you define a different merge strategy for each scenario.

### cluster_config
- `hash_mode`
    - `hash_field`: name of the field used to compute the hash value.
    - `hash_function`: hash function: `HASH`, `HASH64`, `GALAXY_HASH`, `NUMBER_HASH` or `KINGSO_HASH`.
- `builder_rule_config`
    - `partition_count`: number of partitions to build the index into.
    - `build_parallel_num`: number of parallel processes per partition for full builds. Has no effect on incremental builds.
    - `inc_build_parallel_num`: number of parallel processes per partition for incremental builds. Has no effect on full builds.
    - `merge_parallel_num`: default merge parallelism (older way of configuring it). A value set in `offline_index_config` overrides it.
    - `batch_mode`: in build service mode, whether the incremental builder stays resident. If `true`, a build is started at each periodic merge.

### swift_config
`swift_config` configures reads and writes on the intermediate topics that carry processed documents. It may be left empty; in production you can use it to tune swift read and write performance. It only applies outside direct-write mode and can be omitted when direct write is enabled.
- `topic_full` and `topic_inc`: if full and real-time data use different intermediate topics, configure `topic_full` and `topic_inc` separately; otherwise configure only `topic`.
  - `partition_count`: number of partitions in the intermediate topic. More partitions support a higher update rate.
  - `partition_min_buffer_size`: minimum buffer per partition, in MB.
  - `partition_max_buffer_size`: maximum buffer per partition, in MB.
  - `partition_limit`: maximum number of partitions a single swift node can load.
  - `partition_file_buffer_size`: buffer size used when reading cached files.
  - `partition_resource`: resources consumed by one partition; prevents a swift node from loading too many partitions.
  - `obsolete_file_interval`: data expiry time, in hours.
  - `reserved_file_count`: number of cached files. When an intermediate topic has more cached files than this and they have expired, they are cleaned up.
  - `delete_topic_data`: delete the topic's data when the topic is deleted.
  - `topic_mode`: `security`, `memory_prefer` or `normal`. Defaults to `normal`.
    - `security`: synchronous writes. A write returns only after the data is flushed to disk. Data is safe, but write performance suffers.
    - `memory_prefer`: data is normally kept off disk and flushed only when downstream consumers time out. Only takes effect for `topic_full`; not recommended for production.
    - `normal`: data is flushed to disk periodically.

### Direct-write mode
* `direct_write`: `true` or `false`. `true` enables direct-write mode.

#### wal_config: WAL settings in direct-write mode
* `strategy`: WAL strategy. `realtime_swift` (use swift as the WAL) is recommended.
* `sink`
  * `src`: set to `swift`.
  * `type`: set to `swift`.
  * `swift_root`: ZooKeeper address of swift.
  * `topic_name`: swift topic used for the WAL.
  * `writer_config`: parameters for writing to swift for the WAL.

#### realtime_info: how searchers read real-time data in direct-write mode
* `topic_name`: topic used for the WAL; must match `topic_name` in `wal_config`.
* `swift_root`: ZooKeeper address of swift; must match `swift_root` in `wal_config`.
* `reader_config`: settings for reading from swift.
* `realtime_mode`: set to `realtime_service_rawdoc_rt_build_mode`.
