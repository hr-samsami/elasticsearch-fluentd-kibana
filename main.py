from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

response = es.search(index='*', query={"match_all": {}}, scroll='5m', size=1000)

while len(response['hits']['hits']) > 0:
    # Process each document
    for hit in response['hits']['hits']:
        document = hit['_source']
        # Do something with the document
        print(document)

    # Scroll to the next set of results
    scroll_id = response['_scroll_id']
    response = es.scroll(scroll_id=scroll_id, scroll='5m')