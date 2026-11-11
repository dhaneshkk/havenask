---
toc: content
order: 2
---
# Schema configuration
## Structure

A complete `schema.json` file usually contains `columns` and `indexes`.
An example `schema.json`:
```
{
    "columns": [                                        (1)
        {
            "name": "title",
            "type": "TEXT",
            "analyzer": "simple_analyzer"
        },
        {
            "name": "subject",
            "type": "TEXT",
            "analyzer": "simple_analyzer"
        },
        {
            "name": "id",
            "type": "UINT32"
        },
        {
            "name": "hits",
            "type": "UINT32"
        },
        {
            "name": "createtime",
            "type": "UINT64"
        }
    ],
    "indexes": [                                       (2)
        {
            "name": "id",
            "index_config" : {
                "index_fields": [
                    {
                        "field_name": "id"
                    }
                ]
            },
            "index_type": "PRIMARY_KEY64"               (3)
        },
        {
            "name": "id",
            "index_config" : {
                "index_fields": [
                    {
                        "field_name": "id"
                    }
                ]
            },
            "index_type": "ATTRIBUTE"                   (4)
        },
        {
            "name": "hits",
            "index_config" : {
                "index_fields": [
                    {
                        "field_name": "hits"
                    }
                ]
            },
            "index_type": "ATTRIBUTE"
        },
        {
            "name": "createtime",
            "index_config" : {
                "index_fields": [
                    {
                        "field_name": "createtime"
                    }
                ]
            },
            "index_type": "ATTRIBUTE"
        },
        {
            "name": "title",
            "index_config" : {
                "index_fields": [
                    {
                        "field_name": "title"
                    }
                ]
            },
            "index_type": "TEXT"
        },
        {
            "name": "subject",
            "index_config" : {
                "index_fields": [
                    {
                        "field_name": "subject"
                    }
                ]
            },
            "index_type": "TEXT"                        (5)
        },
        {
            "name": "default",
            "index_type": "PACK",
            "index_config": {
                "index_fields": [
                    {
                        "field_name": "title",
                        "boost": 100
                    },
                    {
                        "field_name": "subject",
                        "boost": 200
                    }
                ]
            }
        },
        {
            "name": "summary",
            "index_type": "SUMMARY",                     (6)
            "index_config": {
                "index_fields": [
                    {
                        "field_name": "title"
                    },

                    {
                        "field_name": "subject"
                    },
                    {
                        "field_name": "id"
                    },
                    {
                        "field_name": "hits"
                    },
                    {
                        "field_name": "createtime"
                    }
                ]
            }
        }
    ]
}
    

```

The numbered parts above are:

<1> `columns`: the table's fields.

<2> `indexes`: the index configuration.

<3> `PRIMARY_KEY64`: the table's primary key.

<4> `ATTRIBUTE`: the fields stored as attributes.

<5> `TEXT`: the fields of a text inverted index.

<6> `SUMMARY`: the fields stored in the summary.



## More
- For the field types a schema supports, see [Built-in field types](../../indexes/field-type.md).
- For details on index types, see [Introduction to indexes](../../indexes/intro.md).
