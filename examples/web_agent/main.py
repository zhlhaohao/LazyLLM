import lazyllm
import asyncio
from .fc_tools import build_research_agent, CrawlPagesWorker, LLMWorker, WebSearchWorker, searxng_search
from lazyllm import LOG

async def test():
    links = await searxng_search("广州天气")
    result = await CrawlPagesWorker(links)
    LOG.info(result)


def main():
    main_ppl = build_research_agent()
    lazyllm.WebModule(main_ppl, port=20012).start().wait()     


if __name__ == "__main__":
    # asyncio.run(test())
    asyncio.run(main())    