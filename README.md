# kvlt_parser

pretty simple image parser

### parser.py
opens page with bands, saves name/link pairs into a file, and goes to the next page
uses **Selenium** to deal with tricky ajax pagination

### async_parser.py
takes a file with name/link pairs and tries to save an logo image from each band page
uses **Beautifulsoup** to process pages, **asyncio/aiohttp/aiofiles** to do it asynchronously
