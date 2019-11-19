#!/bin/bash

docker rm --force powerapi-formula
docker rm --force powerapi-sensor

docker pull powerapi/hwpc-sensor
docker pull powerapi/smartwatts-formula

docker run --net=host --privileged --name powerapi-sensor -d \
           -v /sys:/sys -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
           -v /tmp/powerapi-sensor-reporting:/reporting \
		   powerapi/hwpc-sensor:latest \
		   -n "$NAME" \
		   -r "mongodb" -U "$DBURI" -D "$DB" -C "$COLLECTION" \
		   -s "rapl" -o -e "RAPL_ENERGY_PKG" \
		   -s "msr" -e "TSC" -e "APERF" -e "MPERF" \
		   -c "core" -e "CPU_CLK_THREAD_UNHALTED:REF_P" -e "CPU_CLK_THREAD_UNHALTED:THREAD_P" \
                     -e "LLC_MISSES" -e "INSTRUCTIONS_RETIRED"

docker run -td --net=host --name powerapi-formula powerapi/smartwatts-formula \
           -s \
           --input mongodb --model HWPCReport \
                           -u $DBURI -d $DB -c $COLLECTION \
           --output mongodb --name power --model PowerReport \
                            -u $DBURI -d $DB -c $OUTPUT_COL \
           --output mongodb --name formula --model FormulaReport \
                            -u $DBURI -d $DB -c frep \
           --formula smartwatts --cpu-ratio-base $BASE_CPU_RATIO \
                                --cpu-ratio-min $MIN_CPU_RATIO \
                                --cpu-ratio-max $MAX_CPU_RATIO \
                                --cpu-error-threshold 2.0 \
                                --dram-error-threshold 2.0 \
                                --disable-dram-formula
