---
toc: content
order: 3
---

# Analyzer configuration
## Structure
Analyzer configuration has three parts: analyzers, tokenizers, and traditional-to-simplified conversion tables. A complete analyzer configuration file, `analyzer.json`, looks like this:
```
{   
    "analyzers":
    {
        "simple_analyzer":
        {
            "tokenizer_configs" :
            {
                "tokenizer_type" : "simple",
                "delimiter" : " "
            },
            "stopwords" : [],
            "normalize_options" :
            {
                "case_sensitive" : false,
                "traditional_sensitive" : true,
                "width_sensitive" : false
            }
        },
        "singlews_analyzer":
        {
            "tokenizer_configs" :
            {
                "tokenizer_type" : "singlews"
            },
            "stopwords" : [],
            "normalize_options" :
            {
                "case_sensitive" : false,
                "traditional_sensitive" : true,
                "width_sensitive" : false
            }
        },
        "jieba_analyzer":
        {
            "tokenizer_name" : "jieba_analyzer",
            "stopwords" : [],
            "normalize_options" :
            {
                "case_sensitive" : false,
                "traditional_sensitive" : true,
                "width_sensitive" : false
            }
        }
    },
    "tokenizer_config" : {
        "modules" : [
            {
                "module_name": "analyzer_plugin",
                "module_path": "libjieba_analyzer.so",
                "parameters": { }
            }
        ],
        "tokenizers" : [
            {
                "tokenizer_name": "jieba_analyzer",
                "tokenizer_type": "jieba",
                "module_name": "analyzer_plugin",
                "parameters": {
                    "dict_path": "/ha3_install/usr/local/share/jieba_dict/jieba.dict.utf8",
                    "hmm_path": "/ha3_install/usr/local/share/jieba_dict/hmm_model.utf8",
                    "user_dict_path": "/ha3_install/usr/local/share/jieba_dict/user.dict.utf8",
                    "idf_path": "/ha3_install/usr/local/share/jieba_dict/idf.utf8",
                    "stop_word_path": "/ha3_install/usr/local/share/jieba_dict/stop_words.utf8"
                }
            }
        ]
    },
    "traditional_tables": [
        {
            "table_name" : "table_name",
            "transform_table" : {
                "0x4E7E" : "0x4E7E"                                #设置繁体字"乾"不会被转换成简体字
            }
        }
    ]
}
```
### analyzers
Configures the analyzers available for building indexes and for queries. The key is the analyzer name and the value is its configuration. An analyzer can have:
- `tokenizer_configs`: configuration of the tokenizer the analyzer uses.
  - `tokenizer_type`: type of the built-in tokenizer. Any other parameters also go in `tokenizer_configs`, such as `delimiter` for the simple tokenizer.
- `tokenizer_name`: if the analyzer's tokenizer is not built in, configure it in `tokenizer_config` and reference it here by name. Do not use `tokenizer_configs` and `tokenizer_name` together.
- `stopwords`: stop-word list. Any strings, or empty.
- `case_sensitive`: whether case matters. If `true`, the original text is kept; otherwise it is lowercased.
- `traditional_sensitive`: whether traditional vs. simplified Chinese matters. If `true`, the original text is kept; otherwise it is converted to simplified Chinese.
- `width_sensitive`: whether full-width vs. half-width characters matter. If `true`, the original text is kept; otherwise it is converted to half-width.

### tokenizer_config
Configures extension tokenizers: mainly the shared library that provides the tokenizer and its parameters.
- `modules`: shared libraries that provide tokenizers. Can be empty (`[]`) if only built-in analyzers are used.
  - `module_name`: name of the library inside the engine; must start with a letter or underscore.
  - `module_path`: file name of the library in the plugins directory.
  - `parameters`: parameters passed when the library is opened and the analyzer factory is created.
- `tokenizers`: tokenizer definitions. Can be empty (`[]`) if only built-in analyzers are used.
  - `tokenizer_name`: tokenizer name; matches `tokenizer_name` in `analyzers`.
  - `tokenizer_type`: tokenizer type. The library creates the tokenizer based on this value, so it must match the tokenizer in the code.
  - `module_name`: one of the modules configured in `modules`; selects which library to use.
  - `parameters`: parameters needed to create the tokenizer.
### traditional_tables
Traditional-to-simplified Chinese conversion tables. Optional; omit if not needed.

- `table_name`: name of the conversion table. When `traditional_sensitive` is `false`, all traditional characters are converted to simplified ones by default; reference a `traditional_table` by `table_name` to keep specific traditional characters from being converted.
- `transform_table`: the traditional-to-simplified character mappings.

## Common analyzers
### jieba analyzer
* The jieba analyzer (`jieba_analyzer`) is built on the open-source jieba Chinese word segmenter.
```
Input:          他来到了网易杭研大厦   ("He came to the NetEase Hangzhou Research building")
jieba analyzer: 他/来到/了/网易/杭研/大厦
```

* For an example, see the [custom analyzer example](https://github.com/alibaba/havenask/tree/main/aios/tools/hape/example/cases/custom_analyzer).

* For the implementation, see the [jieba analyzer source](https://github.com/alibaba/havenask/tree/main/aios/plugins/havenask_plugins/analyzer_plugins).
* Notes
  - This analyzer only works with TEXT fields.

### Simple analyzer
The simple analyzer (`simple`) splits field content (or query terms) on spaces (" "). Use it for special search scenarios the built-in analyzers can't handle; it gives you full control over how text is split.

* Notes
  - This analyzer only works with TEXT fields. Set the analyzer to `simple` in the schema.
  - This analyzer does not support custom segmentation dictionaries.

### Single-character analyzer
The single-character analyzer (`chn_single`) splits Chinese text into individual characters (other runs, such as numbers, stay as words). It suits Chinese search where semantic segmentation isn't needed.
```
Input:                      菊花茶123   ("chrysanthemum tea 123")
single-character analyzer:  菊 花 茶 123
```

* Notes
  - This analyzer only works with TEXT fields. Set the analyzer to `chn_single` in the schema.
  - This analyzer does not support custom segmentation dictionaries.
