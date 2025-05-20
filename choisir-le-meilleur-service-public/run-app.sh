#!/bin/sh
# entrypoint.sh

sleep 30 

# curl -X PUT http://localhost:9200/_cluster/settings -H 'Content-Type: application/json' -d '
# {
#     \"persistent\": {
#     \"cluster.routing.allocation.disk.threshold_enabled\": false
#     }
# }' 

# Run the DB fill script
echo "Running refresh_data.py..."
python refresh_data.py --elastic-search-host $ELASTICSEARCH_HOSTS

# Start the Flask app
echo "Starting Flask app..."
python app.py -d 