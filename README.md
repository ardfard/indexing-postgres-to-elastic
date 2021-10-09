
Example of real-time indexing Postgres tables to Elasticsearch with Debezium, Google PubSub and Dataflow.

# Dependencies

1. docker and docker-compose
2. nix
3. gcloud SDK

# Running example

```
# Assume working directory inside the repo

$ nix-shell

$ docker-compose up

$ python pubsub.py \
    --project=$PROJECT_ID \
    --input_topic=$INPUT_PUBSUB_TOPIC_ID \
    --temp_location=$GCS_TEMP_FOLDER \
    --region=$GCLOUD_REGION \
    --job_name=$DATAFLOW_JOB_NAME 
```
