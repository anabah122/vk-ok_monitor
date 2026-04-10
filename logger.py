import logging

class _NoStatsFilter(logging.Filter):
    def filter(self, record):
        return "/stats/is_data_invalid" not in record.getMessage()

logging.getLogger("uvicorn.access").addFilter(_NoStatsFilter())