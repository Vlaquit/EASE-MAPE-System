#!/bin/bash

docker rm --force powerapi-formula
docker rm --force powerapi-sensor

docker pull powerapi/hwpc-sensor
docker pull powerapi/smartwatts-formula

docker run --net=host --privileged --name powerapi-sensor -d \
           -v /sys:/sys -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
           -v /tmp/powerapi-sensor-reporting:/reporting \
		   powerapi/hwpc-sensor:latest \
		   -n "demo" \
		   -r "mongodb" -U "mongodb://root:password@127.0.0.1:27017" -D "powerapi" -C "sensor" \
		   -s "rapl" -o -e "RAPL_ENERGY_PKG" \
		   -s "msr" -e "TSC" -e "APERF" -e "MPERF" \
		   -c "core" -e "CPU_CLK_THREAD_UNHALTED:REF_P" -e "CPU_CLK_THREAD_UNHALTED:THREAD_P" \
                     -e "LLC_MISSES" -e "INSTRUCTIONS_RETIRED"

docker run -td --net=host --name powerapi-formula powerapi/smartwatts-formula \
           -s \
           --input mongodb --model HWPCReport \
                           -u mongodb://root:password@127.0.0.1:27017 -d powerapi -c sensor \
           --output mongodb --name power --model PowerReport \
                            -u mongodb://root:password@127.0.0.1:27017 -d powerapi -c formula \
           --output mongodb --name formula --model FormulaReport \
                            -u mongodb://root:password@127.0.0.1:27017 -d powerapi -c frep \
           --formula smartwatts --cpu-ratio-base 18 \
                                --cpu-ratio-min 4 \
                                --cpu-ratio-max 40 \
                                --cpu-error-threshold 2.0 \
                                --dram-error-threshold 2.0 \
                                --disable-dram-formula
