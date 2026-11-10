from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.INFO)

import os
import uvicorn
from util.security import server_host

if __name__ == '__main__':
    # Loopback by default; set SERVER_HOST=0.0.0.0 (together with LLM_API_KEY)
    # to expose it. Auto-reload is a development feature, opt in with RELOAD=1.
    uvicorn.run("server.server:app", host=server_host(), port=int(os.environ.get('SERVER_PORT', 8000)),
                reload=os.environ.get('RELOAD') == '1')
