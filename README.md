# UCLL Intranet RSS Feed
A Slack RSS feed for the messages on [intranet.ucll.be](https://intranet.ucll.be).

The slack branch has &lt;p&gt; and &lt;/br&gt; elements included in the description for formatting.

## RSS Generator
```python
python rss.py -u [UCLL username] -p [UCLL password] -o [Output File] -i [Initialise database]
```

| Argument  | Type |  Description | Required |
| ------------- | ------------- | ------------- | ------------- |
| u  | String  | Your UCLL username (r-number)  | Content Cell  |
| p  | String  | Your UCLL password  | Content Cell  |
| o  | String  | The absolute or relative path to the output file. If it doesn't exist it will be created  | Content Cell  |
| i  | Boolean  | When you set this value to True the database will be created. All the items until now will be fetched and inserted into the database. **It is important that you set this value the first time and that you set it back to False or just remove from the line after the first time.**  | False  |

## RSS Feed
[rss.davidopdebeeck.be/ucll-slack.xml](http://rss.davidopdebeeck.be/ucll-slack.xml)