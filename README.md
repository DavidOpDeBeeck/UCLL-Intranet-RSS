# UCLL Intranet RSS Feed
A RSS feed for the messages on [intranet.ucll.be](https://intranet.ucll.be).

The slack branch has spaces after &lt;p&gt; and &lt;/br&gt; elements for formatting.

## RSS Generator
```python
python rss.py -u [UCLL username] -p [UCLL password] -o [Output File] -i [Initialise database]
```

| Argument  | Type |  Description | Required |
| ------------- | ------------- | ------------- | ------------- |
| u  | String  | Your UCLL username (r-number)  | Yes  |
| p  | String  | Your UCLL password  | Yes  |
| o  | String  | The absolute or relative path to the output file. If it doesn't exist it will be created  | Yes  |
| i  | Boolean  | When you set this value to True the database will be created. All the items until now will be fetched and inserted into the database. **It is important that you set this value the first time and that you set it back to False or just remove from the line after the first time.**  | No  |

## RSS Feeds
[rss.davidopdebeeck.be/ucll.xml](http://rss.davidopdebeeck.be/ucll.xml)
[rss.davidopdebeeck.be/ucll-slack.xml](http://rss.davidopdebeeck.be/ucll-slack.xml)