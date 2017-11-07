# bit_digger

## Requirements

### Python Version

2.7.13

### Packages

```bash
pip install sqlalchemy sqlalchemy_utils ccxt
```

### Environemnt Vars

Necessary Environment Variables
+ BIT_DIGGER_EXCHANGE 
+ BIT_DIGGER_RESOURCE
+ BID_DIGGER_FROM_TIMESTAMP (only used for candles currently)
+ BIT_DIGGER_ENV

If BIT_DIGGER_ENV is production the following are necessary:

+ BIT_DIGGER_SQL_USERNAME
+ BIT_DIGGER_SQL_PASSWORDN
+ BIT_DIGGER_SQL_HOSTNAME
+ BIT_DIGGER_SQL_PORT
+ BIT_DIGGER_SQL_DB_NAME

Either set the variables youself or you can edit the setup.sh appropriately

```bash
# Exchange
# options: exchanges supported by ccxt
export BIT_DIGGER_EXCHANGE=gdax

# Resource
# options: orders, trades, candles
export BIT_DIGGER_RESOURCE=orders

# Environment
# options: test, production
export BIT_DIGGER_ENV=test

# SQL Configuration
# note: only used if environment is production
export BIT_DIGGER_SQL_USERNAME=admin
export BIT_DIGGER_SQL_PASSWORD=password
export BIT_DIGGER_SQL_HOSTNAME=localhost
export BIT_DIGGER_SQL_PORT=3306
export BIT_DIGGER_SQL_DB_NAME=bit_digger
```

then run

```bash
source setup.sh
```

### Usage

Once the environment variables are set execute bit_digger.py

```bash
python bit_digger.py
```