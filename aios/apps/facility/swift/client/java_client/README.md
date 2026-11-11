English | [简体中文](README.zh-CN.md)

## Build steps

- 1. Install [protobuf 2.5.0](https://github.com/protocolbuffers/protobuf/releases/tag/v2.5.0), used to generate Java from the proto files.
- 2. In `pom.xml`, set the protobuf path and the absolute path of `depend_proto`.
- 3. Compile with `sudo mvn compile`.
- 4. Package with `sudo mvn package` (add `-Dmaven.test.skip=true` to skip unit tests), then `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:./`.
- 5. Upload the Java package.


## Run the jar
- `java -Xbootclasspath/a:./protobuf-java-2.5.0.jar:./jna-4.2.1.jar:./swift_client-1.1.0.jar  com.alibaba.search.swift.perf.SwiftClientWriteReadPerf`
- You may hit a wrong ZooKeeper address or a missing alog configuration file.
- If several people run it at the same time, they will use the same topic.

Advanced usage, with arguments `client_config message_size reader_config writer_config`:

    java -Xbootclasspath/a:./protobuf-java-2.5.0.jar:./jna-4.2.1.jar:./swift_client-1.1.0.jar  com.alibaba.search.swift.perf.SwiftClientWriteReadPerf "zkPath=zfs://10.101.170.89:12181,10.101.170.90:12181,10.101.170.91:12181,10.101.170.92:12181,10.101.170.93:12181/swift/swift_service;logConfigFile=./swift_alog.conf;useFollowerAdmin=false" 10 topicName=sdd_test1 "topicName=sdd_test1;functionChain=HASH,hashId2partId##topicName=sdd_test2;;functionChain=HASH,hashId2partId"

Useful JVM options:

    -Djna.debug_load=true  # print which shared libraries are loaded
    -Djna.tmpdir=/ssd/sdd/git/swift/swift_java_client/target/  # set the temporary directory
