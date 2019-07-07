# Aara
> Application to list contract events of the past

### Run via docker
```
docker build -t="aara" .
docker run -it -e "WEB3_INFURA_API_KEY=foo" -e "WEB3_INFURA_API_SECRET=bar" -p 8080:8080 aara
visit: http://127.0.0.1:8080/
```

### Run via python
Environment variables can alternatively be set in .bashrc file
```
pip3 install -r requirements.txt
export FLASK_APP=api.py
export DEBUG=1
flask run
```

### Tests
Refer to [testing guide](https://github.com/samar-agrawal/aara/tree/master/tests)
```
docker run -it -e "WEB3_INFURA_API_KEY=foo" -e "WEB3_INFURA_API_SECRET=bar" aara pytest
```
