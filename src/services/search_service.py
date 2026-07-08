from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
import logging
import concurrent.futures

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.ddg = DuckDuckGoSearchRun()

    def search(self, query: str) -> str:
        """
        Executes a web search for the given query and returns the results as a string.
        """
        logger.info(f"Searching for: {query}")
        try:
            results = self.ddg.run(query)
            return results
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return ""

    def batch_search(self, queries: list[str]) -> list[str]:
        """
        Executes multiple web searches in parallel for the given list of queries.
        """
        logger.info(f"Batch searching for {len(queries)} queries...")
        # Using a ThreadPoolExecutor to run searches in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(self.search, queries))
        return results

search_service = SearchService()
