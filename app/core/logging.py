import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    filename=r"logs/app.log"
)

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)