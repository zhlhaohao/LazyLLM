import os
import time
import jwt
from .openaiModule import OpenAIModule


class UniinModule(OpenAIModule):
    def __init__(
        self,
        base_url: str = "https://openai.uniin.cn/openapi/v1/",
        model: str = "qwen3-32b",
        api_key: str = None,
        stream: bool = True,
        return_trace: bool = False,
        **kwargs,
    ):
        # 千问模型在uniin中就算是非流式问答也必须采用流式方式
        if "qwen" in model.lower():
            stream = True

        OpenAIModule.__init__(
            self,
            base_url=base_url,
            model=model,
            stream=stream,
            return_trace=return_trace,
            **kwargs,
        )

    def _set_headers(self):
        exp_seconds = 3600000
        app_key = os.getenv("UNIIN_APP_KEY", "")
        app_secret = os.getenv("UNIIN_APP_SECRET", "")
        now = int(round(time.time()))
        payload = {"app_key": app_key, "exp": now + exp_seconds, "iat": now}
        token = jwt.encode(
            payload,
            app_secret,
            algorithm="HS256",
            headers={"alg": "HS256", "typ": "JWT"},
        )

        self._headers = {
            "Content-Type": "application/json",
            "Authorization": token,
            "Accept": "text/event-stream",
        }
