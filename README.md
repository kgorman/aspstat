# aspstat
An iostat like tool for Atlas Stream Processing

## Getting Started
### Install python3 dependencies
```
pip3 install -r requirements.txt
```

### Create an Atlas API Key
_aspstat_ utilizes an Atlas API key to query the Atlas Stream Processing AdminAPI. Follow the Atlas documentation to generate an API Key and Secret for use

[Grant Programmatic Access to a Project
](https://www.mongodb.com/docs/atlas/configure-api-access/#grant-programmatic-access-to-a-project)


### Export the key as OS environmental variables 
```
export ATLAS_USER=YOURPUBLICAPIKEY
export ATLAS_USER_KEY=YOURPRIVATEAPIKEY
```

### Fetch groupid and instance name
The groupid can be found in the URL when visiting the Atlas UI and is the string located between v2/**65094f059e0776665611599b**/
```https://cloud.mongodb.com/v2/65094f059e0776665611599b#/streamProcessing```

The instance name is the name that the Stream Processing Instances was given when it was created

### Run aspstat
```
usage: aspstat.py [-h] --group GROUP --instance INSTANCE
python3 aspstat.py --group 65094f059e0776665611599b --instance myaspinstance

Proc Fail Input Count  Input Size   Output Count Output Size  DLQ    State Size   opTime kIdle  kLag  
3    0    7.0          2587.0       3.0          1422.0       0.0    0.0          0      12     0     
3    0    7.0          2607.0       3.0          1433.0       0.0    0.0          0      24     0     
3    0    7.0          2608.0       3.0          1433.0       0.0    0.0          0      36     0
```


## Metric Definitions
- **proc**
    - Number of Stream Processors in "Started" state
- **fail**
    - Number of Stream Processors in "Failed" state
- **Input Count**
    - per second inputMessageCount of all Started and Failed Stream Processors
- **Input Size**
    - per second inputMessageSize in bytes of all Started and Failed Stream Processors
- **Output Count**
    -per second outputMessageCount of all Started and Failed Stream Processors
- **Output Size**
    - per second outputMessageSize in bytes of all Started and Failed Stream Processors
-  **DLQ**
    - per second dlqMessageCount of all Started and Failed Stream Processors
- **State Size**
    - per second number of bytes used by windows to store processor state
- **opTime**
    - The 5 moving minute average events take to be processed in milliseconds
- **kIdle**
    - The number of Kafka Partitions being read by processors that are Idle
- **kLag**
    - The total consumer lag for processors using Kafka Sources

