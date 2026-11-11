---
toc: content
order: 10
---

# Engine development

## Offline plugin development
* For offline data-processing plugins, see `aios/apps/facility/build_service/build_service/processor/BuildInDocProcessorFactory.cpp`.
* For offline analyzer (tokenizer) plugins, see `aios/plugins/havenask_plugins/analyzer_plugins`.

## Online UDF plugin development
* See `aios/plugins/havenask_plugins/udf_plugins`. After writing an online UDF plugin, you must rebuild your own runtime image.
* Suppose you want to implement a UDF `sumOf` that adds the values of two input fields and returns the result:

```sql
SELECT brand, sumOf(price, size) as sumOf FROM phone where brand='Xiaomi' ORDER BY price LIMIT 100
```

### Implementation

You mainly need to implement two functions:

- `beginRequest`: called when the query starts. Initialize anything needed later here.
- `evaluate`: called during execution with the relevant fields of each document; its return value is the result.
```cpp
template<typename T>
class SumOfFunction : public FunctionInterfaceTyped<T>
{
public:
    bool beginRequest(suez::turing::FunctionProvider *provider);
    T evaluate(matchdoc::MatchDoc matchDoc);
};
```


For this example, `evaluate` only needs to add the field values. (Note: call `evaluate` on each `AttributeExpression` before using `getValue` to read the field value.)
```cpp
template<typename T>
class SumOfFunction : public FunctionInterfaceTyped<T>
{
// some code omitted
public:
    bool beginRequest(suez::turing::FunctionProvider *provider) {
        return true;
    }
    T evaluate(matchdoc::MatchDoc matchDoc) {
        T value = T();
        for (size_t i = 0; i < _pAttrVec->size(); ++i) {
            (void)(*_pAttrVec)[i]->evaluate(matchDoc);
            value += (*_pAttrVec)[i]->getValue(matchDoc);
        }
        return value;
    }
private:
    std::vector<search::AttributeExpressionTyped<T>*> *_pAttrVec;
// some code omitted
};
```

### Register the plugin

After implementing the UDF, you must configure it before it can be used.

#### Register the UDF
Register the function in `aios/plugins/havenask_plugins/udf_plugins/HavenaskUdfFactory.cpp`:
```cpp
bool HavenaskUdfFactory::registeFunctions() {
    REGISTE_FUNCTION_CREATOR(VectorScoreFunctionCreatorImpl);
    REGISTE_FUNCTION_CREATOR(BM25ScoreFunctionCreatorImpl);
    REGISTE_FUNCTION_CREATOR(TfIdfScoreFunctionCreatorImpl);
    // add yours here
    REGISTE_FUNCTION_CREATOR(SumOfFunctionCreatorImpl);
    return true;
}
```


#### Declare the UDF prototype

Register the UDF prototype in `aios/sql/misc/sql_function.json`:
```json
{
    "functions": [
        {
            "function_name": "sumOf",                      // 1
            "function_type": "UDF",                         // 2
            "is_deterministic": 1,                          // 3
            "function_content_version": "json_default_0.1", 
            "function_content": {
                "properties" : {},                          // 4
                "prototypes": [                             // 5
                    {
                        "params": [                         // 6
                            {
                                "is_multi": false,
                                "type": "double"
                            },
                            {
                                "is_multi": false,
                                "type": "double"
                            }
                        ],
                        "returns": [                        // 7
                            {
                                "is_multi": false,
                                "type": "double"
                            }
                        ]
                    }
                ]
            }
        }
    ]
}
```

Notes:

1. The name of the registered plugin.
2. The type of the registered plugin: `UDF`.
3. `is_deterministic`: whether the function always returns the same output for the same input. `0` means non-deterministic and `1` means deterministic. Deterministic functions allow more optimizations, such as push-down execution.

     Example: `random()` returns a different value on every call, so its `is_deterministic` is `0`.

4. Additional information for registering the plugin.
5. A plugin can register multiple function prototypes; each prototype is a map.
6. The parameter list.
7. The return type.


## Debugging and deployment
### Debugging
* Create an `ha3_dev` container, log in to it, and compile the code with the `./build.sh` script in the repository root.
* Developers usually build havenask or plugins in the `ha3_dev` image, so a standalone `ha3_runtime` image cannot be used to test the latest code directly. To work around this, set `processorMode` in `global.conf` → `common` to `proc` (see [hape configuration](./config/hape-config.md)). hape commands then run your latest local build instead of the older code inside the runtime image.

### Deployment
* Build your own runtime image with `docker/havenask/runtime/Dockerfile` in the repository root.
* In `/ha3_install/hape_conf`, replace `image` in `global.conf` with your own runtime image.
