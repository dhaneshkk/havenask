---
toc: content
order: 1
---
# data_table configuration
## Introduction
The $table_name_table.json file describes the details of how the raw data is processed, where $table_name is the name of the data table, which is generally the same as the index table. The configuration file consists of three parts: processor_chain_config, processor_config, and processor_rule_config. processor_chain_config configures the specific data processing logic, processor_config sets the number of threads and queue size for data processing, and processor_rule_config sets the number and concurrency of data processing nodes. Here is an example of a complete configuration file:
```
{
    "processor_chain_config" : [
        {
            "clusters" : [
                "in0"
            ],
            "document_processor_chain" : [
                {
                    "class_name" : "TokenizeDocumentProcessor",
                    "module_name" : "",
                    "parameters" : {
                    }
                }
            ],
            "modules" : [
            ]
        }
    ],
    "processor_config" : {
        "processor_queue_size" : 2000,
        "processor_thread_num" : 10
    },
    "processor_rule_config" : {
        "parallel_num" : 1,
        "partition_count" : 1
    }
}
```
## Configuration details
### processor_chain_config
processor_chain_config is an array that can contain multiple processing chains. When multiple processing chains exist, it indicates that a piece of data is processed by different processing chains and used for index construction of multiple index tables. The following is the configuration of a processing chain.
```
        {
            "clusters" : [
                "in0"
            ],
            "document_processor_chain" : [
                {
                    "class_name" : "AnyClassName",
                    "module_name" : "example_module",
                    "parameters" : {
                        "param1" : "value1"
                    }
                },
                {
                    "class_name" : "TokenizeDocumentProcessor",
                    "module_name" : "",
                    "parameters" : {
                    }
                }
            ],
            "modules" : [
                {   
                    "module_name" : "example_module",
                    "module_path" : "libExample.so",
                    "parameters" : {
                    }
                }
            ]
        }
```
* `clusters`: which index tables the documents produced by this chain are used to build.
* `document_processor_chain`: the processing steps of this chain. Each processing node takes these parameters:
  * `class_name`: name of the processing node; must match the name set in the node's implementation class.
  * `module_name`: name of the shared library containing the node's class. Leave it empty for built-in nodes; see the `build_service/processor` directory for the nodes the system provides.
  * `parameters`: a key-value map of the node's parameters; values must be strings.
* `modules`: shared libraries of the plugins used in the chain. If every node in the chain is built in, this can be an empty array. (<font color="red">Note: in the current version, custom processor plugins must be defined as built-in plugins; see the processor plugin example.</font>)
  * `module_name`: name of the module; any string, but it must match `module_name` in the processing nodes.
  * `module_path`: path of the shared library, relative to the `plugins` directory in the configuration directory.
  * `parameters`: a key-value map of the library's parameters; values must be strings.

### processor_config
```
{
    "processor_queue_size" : 2000,
    "processor_thread_num" : 10
}
```
* `processor_thread_num`: number of data-processing threads. With enough CPU, more threads process data faster.
* `processor_queue_size`: size of the processing queue. Newly read data waits in this queue; no new data is read while it is full.

### processor_rule_config
```
{
    "parallel_num" : 1,
    "partition_count" : 1
}
```
* `partition_count`: number of data-processing processes. Set it to 1 when building indexes locally.
* `parallel_num`: data-processing parallelism for full builds. A full build starts `parallel_num * partition_count` processing processes. Set it to 1 when building indexes locally.
