Open terminal inside the project folder (Once you type dir you should see the application python files). Then execute following commands.

### Create virtual environment
```shell
python3.8 -m venv venv
```

### Activate virtual environment
```shell
venv\Scripts\activate
```

### Install libraries
```shell
pip install -r requirements.txt
```

### Update Location Keys
* Update [location.json](./locations.json) with the keys words or URLs required to be extracted.
* Logs will be stored in [logs](./logs) directory.
* Scraped data will be stored in [scraped_data](./scraped_data) directory.

### Provide the file path with command
```shell
python main.py
```




