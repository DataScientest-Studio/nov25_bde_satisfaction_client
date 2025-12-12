from es_kibana.jsonl_loader import load_last_jsonl
from es_kibana.elasticsearch_bulk_loader import load_reviews_to_elasticsearch_bulk

documents = load_last_jsonl("es_kibana/data")
load_reviews_to_elasticsearch_bulk(documents=documents)
