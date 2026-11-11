English | [简体中文](README.zh-CN.md)

## Havenask images

### ha3_dev
* `ha3_dev` is built on `os_base` and adds the Google Bazel build tool. Some dependency libraries of havenask have not been open-sourced yet, so they are included in this image as externals.

### ha3_runtime
* `ha3_runtime` is built on `os_base` and adds havenask's runtime dependencies. If you modify the havenask code, build the `hape_tar.tar` target, copy it into the `runtime` directory, and rebuild the runtime image.
