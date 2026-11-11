English | [简体中文](README.zh-CN.md)

# Introduction
This project combines Havenask with large language models, using Havenask as the vector database, to build a document-based question answering system. It can use the ChatGPT service, or run fully on open-source components (ChatGLM-6b) for a private local deployment.

Flow chart:

![Flow chart](resources/flow.jpg)

# Getting started
The simplest way to use Havenask is to create an instance on [Alibaba Cloud OpenSearch](https://www.aliyun.com/product/opensearch); see the [OpenSearch + LLM solution](https://help.aliyun.com/document_detail/2341640.html) (in Chinese).

To deploy Havenask locally, follow the steps below.

## Requirements
* 16 CPU cores, 64 GB of memory
* A GPU with 16 GB of memory
* Docker

## Using the GPU inside a Docker container
To use the GPU inside a Docker container:

1. Docker 19.03 or later.
2. On the host, install:
* [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
* [nvidia-container-runtime](https://github.com/NVIDIA/nvidia-container-runtime#installation)
3. In `docker/havenask/create_container.sh`, add `--gpus all` to the `docker run` command.

## Prepare the container
* Clone the havenask repository
```shell
git clone https://github.com/alibaba/havenask.git
```

* Create the container
```shell
cd ~/havenask/docker/havenask
./create_container.sh havenask registry.cn-hangzhou.aliyuncs.com/havenask/ha3_runtime:latest
```

* Log in to the container
```shell
./havenask/sshme
```

For details, see [havenask](https://github.com/alibaba/havenask#get-started).

## Install dependencies
Manage the Python environment with [conda](https://conda.io/projects/conda/en/stable/user-guide/install/linux.html). Download `Anaconda` for Linux and follow the installer's prompts.

```shell
bash Anaconda3-2023.03-1-Linux-x86_64.sh
```

After installing conda, create and activate a Python environment:
```shell
source ~/.bashrc
conda create --name havenask_llm python=3.10
conda activate havenask_llm
```

Install the Python dependencies:
```shell
cd ~/havenask/llm  # the current directory is /home/$USER
pip install -r requirements.txt
```

## Configuration
Configure the model settings in the `.env` file.

* Using ChatGPT
```conf
LLM_NAME=OpenAI

OPENAI_API_KEY=***
OPENAI_API_BASE=***

OPENAI_EMBEDDING_ENGINE=text-embedding-ada-002
OPENAI_CHAT_ENGINE=gpt-3.5-turbo

VECTOR_STORE=Havenask
HA_QRS_ADDRESS=127.0.0.1:45800
HA_TABLE_NAME=llm
```

* Using Microsoft Azure OpenAI
```conf
LLM_NAME=OpenAI

OPENAI_API_KEY=***
OPENAI_API_BASE=***
OPENAI_API_VERSION=2023-03-15-preview
OPENAI_API_TYPE=azure

# Your Azure OpenAI model deployments
OPENAI_EMBEDDING_ENGINE=embedding_deployment_id
OPENAI_CHAT_ENGINE=chat_deployment_id

VECTOR_STORE=Havenask
# Havenask settings
HA_QRS_ADDRESS=127.0.0.1:45800
HA_TABLE_NAME=llm
```

* Using ChatGLM-6b
```conf
LLM_NAME=ChatGLM

VECTOR_STORE=Havenask
HA_QRS_ADDRESS=127.0.0.1:45800
HA_TABLE_NAME=llm

# Model service addresses (optional)
#CHATGLM_SERVER_ENDPOINT=http://127.0.0.1:8001/
#EMBEDDING_SERVER_ENDPOINT=http://127.0.0.1:8008/

# Open-source model names; if no service address is set, the models are loaded locally
EMBEDDING_MODEL=GanymedeNil/text2vec-large-chinese
CHATGLM_MODEL=THUDM/chatglm-6b
```

### Security
Services bind to `127.0.0.1` by default. To expose them, set both `SERVER_HOST` and `LLM_API_KEY`; an unauthenticated server on a non-loopback address refuses to start.

```
# Bind address (default 127.0.0.1)
#SERVER_HOST=0.0.0.0
# API key: requests must send "Authorization: Bearer <key>" or "X-API-Key: <key>"; web_demo uses it as the login password
#LLM_API_KEY=change-me
# Maximum upload size in bytes (default 20 MiB)
#MAX_UPLOAD_BYTES=20971520
# Maximum topn per query (default 50)
#MAX_TOPN=50
# trust_remote_code runs code from the model repository: pin a commit you have reviewed
#CHATGLM_REVISION=<commit sha>
# Auto-reload, for development only
#RELOAD=1
```

Run the tests: `pip install -r tests/requirements-test.txt && python -m pytest tests`

## Build the knowledge base
Process your data files with [embed_files.py](script/embed_files.py). It currently supports `.md` and `.pdf` files and produces a data file in Havenask engine format.
For example, to process the Havenask wiki while skipping files under `.git` and `english`:
```shell
git clone https://github.com/alibaba/havenask.wiki.git
python -m script.embed_files -f havenask.wiki -o ./llm.data -i .git,english
```

* `-f` sets the directory of documents to process.

If downloading the models from `Huggingface` fails, download them manually; see [Load models locally](#load-models-locally).

### Build the index and start the service
Copy the generated `llm.data` to `/ha3_install/example/data/llm.data` and start the havenask service; the case script writes the data into the engine. Change the port if needed, and update the QRS port in `.env` to match.

```shell
cp ./llm.data /ha3_install/example/data/llm.data
/ha3_install/example/common/case.py run --case llm
```
* The Havenask service currently needs Python 2.7 to start these tasks.

## Start the Q&A service
### API
```shell
cd ~/havenask/llm
python api_demo.py
```
Test request ("havenask是什么" means "What is havenask?"; the default models and knowledge base are Chinese):
```shell
curl -H "Content-Type: application/json" http://127.0.0.1:8000/chat -d '{"query": "havenask是什么"}'
```
If you set `LLM_API_KEY`, add `-H "Authorization: Bearer <key>"`.

Output (abridged; the answer says that havenask is a distributed system developed by Alibaba that supports SQL queries and built-in and plugin UDFs, and can be deployed with the distributed operations tool):
```json
{
    "success":true,
    "result":"havenask 是一个分布式数据库管理系统，由阿里巴巴开发。它支持 SQL 查询语句，并提供了内置的 UDF(User Defined Function)功能，允许客户以插件形式开发自己的 UDF。...",
    "history":[
        [
            "已知信息：\n                Content: ... 问题是：havenask是什么",
            "havenask 是一个分布式数据库管理系统，由阿里巴巴开发。..."
        ]
    ],
    "source":["快速开始.md","UDF.md","Havenask分布式运维工具.md"],
    "finished":true
}
```

### CLI
```shell
cd ~/havenask/llm
python cli_demo.py
```
Type `exit` to quit, `clear` to clear the history, or anything else to ask a question.
![cli-demo](resources/clidemo.jpg)

### Web demo
```shell
cd ~/havenask/llm
python web_demo.py
```
Open the printed web address in your browser.
![web-demo](resources/webdemo.jpg)

# FAQ
## Deploy the models remotely
For the resources ChatGLM-6b needs, see the [official documentation](https://github.com/THUDM/ChatGLM-6B#%E4%BD%BF%E7%94%A8%E6%96%B9%E5%BC%8F).

If the local machine lacks resources, you can deploy the models remotely, for example on a GPU ECS instance. See the deployment scripts [deploy_embedding.py](script/deploy_embedding.py) and [deploy_chatglm.py](script/deploy_chatglm.py). They download the model files from `huggingface` automatically and depend on `torch` and `transformers`.

* Deploy the embedding model
```shell
python script/deploy_embedding.py
```
Default port: 8008

* Deploy ChatGLM-6b
```shell
python script/deploy_chatglm.py
```
Default port: 8001

Both servers listen on `127.0.0.1` and have no authentication. To reach them from another machine, set `SERVER_HOST` and put them behind a network you trust.

* Update the service addresses in `.env`
```conf
CHATGLM_SERVER_ENDPOINT=http://{ip}:8001/
EMBEDDING_SERVER_ENDPOINT=http://{ip}:8008/
```

## Change the models

By default this project uses the [ChatGLM-6b](https://huggingface.co/THUDM/chatglm-6b) LLM and the [GanymedeNil/text2vec-large-chinese](https://huggingface.co/GanymedeNil/text2vec-large-chinese) embedding model.

To change models, set the model names in `.env` and add an adapter in `llm_adapter` that loads the new model; see [local_chatglm.py](llm_adapter/local_chatglm.py), and [deploy_chatglm.py](script/deploy_chatglm.py) for remote deployment.

Different embedding models produce embeddings of different dimensions, so update the dimension in the havenask configuration by changing `dimension` in:
```
/ha3_install/example/cases/llm/in0_schema.json
```

## Load models locally
The code uses `transformers` to download models from Hugging Face automatically. On a poor network, downloads can be slow or time out. You can download the models to a local directory and load them from there.

* Install [Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage)
* Download the models from Hugging Face:
```shell
cd ~/havenask
git clone https://huggingface.co/THUDM/chatglm-6b
git clone https://huggingface.co/GanymedeNil/text2vec-large-chinese
```
* In `.env`, replace the model names with their local **absolute paths**, for example:
```
EMBEDDING_MODEL=/home/{USER}/havenask/text2vec-large-chinese
CHATGLM_MODEL=/home/{USER}/havenask/chatglm-6b
```
Replace `USER` with your actual user name; the model directories must be absolute paths.

## Change how files are split into chunks
By default, files are split by token count with overlap. To implement a different splitter, see [sentence_spliter.py](spliter/sentence_spliter.py).

# Important notice
The "open-source embedding models", "large language models (such as ChatGPT)" and similar components in this solution come from third parties (together, "third-party models"). Alibaba cannot guarantee that third-party models are compliant or accurate, and takes no responsibility for the third-party models themselves or for your use of them and its results. Please consider carefully before accessing and using them.

Third-party models also come with their own open-source licenses and other agreements. Read them carefully and comply with them strictly.
