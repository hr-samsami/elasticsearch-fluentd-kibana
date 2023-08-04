## Fluentd with Elasticsearch, Kibana and Apache HTTP server 

### Docker-compose.yml
```
version: '3'
services:
  web:
    image: httpd:2.4
    ports:
      - "80:80"
    depends_on:
      fluentd:
        condition: service_healthy
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: httpd.access

  fluentd:
    build: ./fluentd
    volumes:
      - ./fluentd/conf:/opt/bitnami/fluentd/conf
    depends_on: 
      kibana:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "netstat", "-l", "|", "grep", "24224"]
      interval: 30s
      timeout: 10s
      retries: 10   
    ports:
      - "24224:24224"
      - "24224:24224/udp"
      
  elasticsearch:
    image: docker.io/bitnami/elasticsearch:8
    environment:
      - "discovery.type=single-node"
    expose:
      - "9200"
    ports:
      - "9200:9200"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9200"]
      interval: 30s
      timeout: 10s
      retries: 5

  kibana:
    image: docker.io/bitnami/kibana:8
    ports:
      - "5601:5601"
    depends_on:
      elasticsearch:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5601"]
      interval: 30s
      timeout: 10s
      retries: 5
```
### fluent.conf
```
<source>
  @type forward
  port 24224
  bind 0.0.0.0
</source>

<match *.**>
  @type copy

  <store>
    @type elasticsearch
    host elasticsearch
    port 9200
    logstash_format true
    logstash_prefix fluentd
    logstash_dateformat %Y%m%d
    include_tag_key true
    type_name access_log
    tag_key @log_name
    flush_interval 1s
  </store>

  <store>
    @type stdout
  </store>
</match>
```
### Dockerfile 
```
FROM bitnami/fluentd:1.16.2

USER root

RUN apt update \
 && apt install -y net-tools

USER daemon
```

### Command
`docker-compose up -d`

If you alreay have the image and just want to rebuild fluentd with the new debian and gem version run:  
`docker-compose up -d --build`

To generate some logs
`repeat 100 curl localhost`

### Site Info
http://localhost:5601