import lazyllm
import asyncio
from .fc_tools import build_web_search_agent, CrawlPagesWorker, LLMWorker, WebSearchWorker, searxng_search
from lazyllm import LOG

async def test():
    links = await searxng_search("广州天气")
    result = await CrawlPagesWorker(links)
    LOG.info(result)


def main():
    main_ppl = build_web_search_agent()

    # # 图形化界面
    # lazyllm.WebModule(main_ppl, port=20012).start().wait()     

    query = "今天广州的天气如何？"
    with lazyllm.ThreadPoolExecutor(1) as executor:
        future = executor.submit(main_ppl, query)
        buffer = ""
        while True:
            if value := lazyllm.FileSystemQueue().dequeue():
                buffer += "".join(value)
                print(f"\n\n流式输出:\n{buffer}")
            elif value := lazyllm.FileSystemQueue().get_instance('lazy_trace').dequeue():
                print(f"\n\n中间跟踪:\n{''.join(value)}")
            elif future.done():
                break
        print(f"\n\n最终回答:\n{future.result()}")



if __name__ == "__main__":
    # asyncio.run(test())
    # asyncio.run(main())    
    main()