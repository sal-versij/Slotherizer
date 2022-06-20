FROM docker.elastic.co/logstash/logstash:8.2.0
RUN rm -f /usr/share/logstash/pipeline/logstash.conf
RUN rm -f /usr/share/logstash/config/logstash.yml
COPY pipeline/*.conf /usr/share/logstash/pipeline/
COPY config/*.yml /usr/share/logstash/config/