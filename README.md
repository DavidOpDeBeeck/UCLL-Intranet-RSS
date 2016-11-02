# UCLL Intranet RSS Feed

A RSS feed for the messages on [intranet.ucll.be](https://intranet.ucll.be).

## RSS Generator

### Command-line

```python
python rss.py [...arguments]
```

### Arguments

##### -u, --username (required)

Your UCLL username (r-number).

##### -p, --password (required)

Your UCLL password.

##### -o, --output (required)

The absolute or relative path to the output file. If it doesn't exist it will be created. If it already exist it will be overwritten.

##### -f, --format (default=0)

The format of the output file. To support the RSS feed feature in Slack we provide a format that will append a space after the &lt;p&gt; and &lt;/br&gt; element.

- 0 : No formatting.
- 1 : A space will be appended after the &lt;p&gt; and &lt;/br&gt; element.

##### -i, --initialise (default=false)

When you set this value to `true` the database will be created. All the items until now will be fetched and inserted into the database. 

**Note** : It is important that you set this value the first time and that you set it back to `false` or just remove from the line after the first time.
