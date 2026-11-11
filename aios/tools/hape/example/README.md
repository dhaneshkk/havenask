English | [简体中文](README.zh-CN.md)

# Examples
* Run an example case with the command below. By default, examples test with one direct-write table; add `--type offline` to test with a full table instead.
```
/ha3_install/example/common/case.py run --case <case-name>
```

* The cluster is not deleted after an example finishes, so you can keep working with it. For example, after the `normal` case finishes, check the table status with:
```
/ha3_install/example/common/case.py execute --case normal --command "hape gs table"
```
* You can also keep reading and writing data, for example:
```
/ha3_install/sql_query.py --query "select * from in0" 
```


## Available examples


| Case  |  Description |
|---|---|
| normal | Default example; runs simple SQL queries  |
| vector | havenask vector index example |
| custom_analyzer | Custom havenask analyzer plugin built on the open-source C++ jieba tokenizer |
| llm | Vector table used by the [LLM question answering demo](../../../../llm/README.md) |


## Directory layout
* `data`: test data
* `common`: test tool scripts
* `cases`: example cases
* `cases/<case>`: one example case
  * `setup.py`: metadata for running the case, including which hape configuration it uses (`hape_conf/<name>`)
  * `xx_schema.json`: the table schema for the case
