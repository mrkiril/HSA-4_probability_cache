### UP TIG (Telegraf - InfluxDB - Grafana)
### And services which want to monitoring (nginx mysql redis elasticsearch mongo)
## Usage
### Development

### Pre-Setting

Off elastic documentation say to up `vm.max_map_count=262144` [look here!](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_set_vm_max_map_count_to_at_least_262144)
check it

### RUN  services
```
make run
``` 

###To rum ApacheBenchmark set it like [here](https://ourcodeworld.com/articles/read/957/how-to-run-a-stress-test-to-your-apache-server-in-ubuntu-18-04)
```
sudo apt-get install apache2-utils
```

###Run AB for elastic or nginx:
```
make test_elastic
make test_nginx
```