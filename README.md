# slacklogs2mongo
Import exported Slack logs into MongoDB

## Example usage

```sh
./slacklogs2mongo.py --logs /tmp/slacklogs --mongo mongodb://your.mongo.server.com/slack
```
`/tmp/slacklogs` is where you extracted the log archive you downloaded from the export page in the Slack admin panel.
The `--mongo` option lets you specify the connection string for your MongoDB server. If you do not specify the database the data will be imported into the default database. This script will put messages from all channels into a single collection (`messages`). Channel name and ID can be found in fields `channel_name` and `channel`, respectively.
The name of the MongoDB database does not _have_ to be `slack`, of course.

