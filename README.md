# aon_backend


### post comment
* request
``` shell
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"token":"0x54791a2d86e73b5f24c7921816e9251ca191c3d3", "createdBy":"0xb492192a8793ec8c2c00379a6de6c9dac8f3bc91", "content":"content by 0xb492192a8793ec8c2c00379a6de6c9dac8f3bc91"}' \
http://127.0.0.1:8080/comment/post
```
* response
``` json
{
  "code": 0,
  "data": null,
  "lang": "en",
  "msg": "success"
}
```


### list comment
* request
``` shell
curl -X GET -H "Content-Type: application/json" "http://127.0.0.1:8080/comment/list?token=0x54791a2d86e73b5f24c7921816e9251ca191c3d3"
```
* response
``` json
{
  "code": 0,
  "data": [
    {
      "content": "content by 0xb492192a8793ec8c2c00379a6de6c9dac8f3bc91 ....",
      "contract": "0x54791a2d86e73b5f24c7921816e9251ca191c3d3",
      "creator": "0xb492192a8793ec8c2c00379a6de6c9dac8f3bc91",
      "ctime": "2025-01-09 13:37:59",
      "id": 3
    },
    {
      "content": "content by 0xb492192a8793ec8c2c00379a6de6c9dac8f3bc91",
      "contract": "0x54791a2d86e73b5f24c7921816e9251ca191c3d3",
      "creator": "0xb492192a8793ec8c2c00379a6de6c9dac8f3bc91",
      "ctime": "2025-01-09 13:27:32",
      "id": 2
    }
  ],
  "lang": "en",
  "msg": "success"
}
```

### recently trade(tx)
* request
``` shell
curl -X GET -H "Content-Type: application/json" "http://127.0.0.1:8080/tx/recently?token=0x54791a2d86e73b5f24c7921816e9251ca191c3d3"
```
* response
``` json
{
  "code": 0,
  "data": [
    {
      "aonFee": "0.000000160054685597",
      "ctime": "2025-01-09 08:54:58",
      "ethPrice": "3244.000000000000000000",
      "id": "0xc0e99fa5544cac39bdbc0d90e1f034bcfa04b903564d2fc924b64c6a13976966-105",
      "index": 3,
      "isBuy": true,
      "price": "0.000005192174000864",
      "qty": "10000.000000000000000000",
      "quoteQty": "0.000016005468559791",
      "token": "0x54791a2d86e73b5f24c7921816e9251ca191c3d3",
      "trader": "0x76b713f30734450ce566c170fda27e8dce63b1f6",
      "txId": "0xc0e99fa5544cac39bdbc0d90e1f034bcfa04b903564d2fc924b64c6a13976966"
    },
    {
      "aonFee": "0.000001000000000000",
      "ctime": "2025-01-09 08:54:58",
      "ethPrice": "3244.000000000000000000",
      "id": "0xb2fbc99e3beacfbdb8c0a2b7c69af4e0906eb5d93649dd5f4ea6be803efdd334-61",
      "index": 2,
      "isBuy": true,
      "price": "0.000005244228817668",
      "qty": "61858.475547085610000000",
      "quoteQty": "0.000100000000000000",
      "token": "0x54791a2d86e73b5f24c7921816e9251ca191c3d3",
      "trader": "0x76b713f30734450ce566c170fda27e8dce63b1f6",
      "txId": "0xb2fbc99e3beacfbdb8c0a2b7c69af4e0906eb5d93649dd5f4ea6be803efdd334"
    },
    {
      "aonFee": "0.000001000000000000",
      "ctime": "2025-01-09 08:54:58",
      "ethPrice": "3244.000000000000000000",
      "id": "0x7928d09d2a87dc86840a4fb7a08bc34939353779b51aae52b999a8a2b1d637b0-31",
      "index": 1,
      "isBuy": true,
      "price": "0.000005243295116612",
      "qty": "61869.490977180925000000",
      "quoteQty": "0.000100000000000000",
      "token": "0x54791a2d86e73b5f24c7921816e9251ca191c3d3",
      "trader": "0xb492192a8793ec8c2c00379a6de6c9dac8f3bc91",
      "txId": "0x7928d09d2a87dc86840a4fb7a08bc34939353779b51aae52b999a8a2b1d637b0"
    }
  ],
  "lang": "en",
  "msg": "success"
}
```

### create token

* request

``` shell

curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"AI Agent","symbol":"MTK","image":"http://gips3.baidu.com/it/u=119870705,2790914505&fm=3028&app=3028&f=JPEG&fmt=auto?w=1280&h=720","contract":"0x54791a2d86e73b5f24c7921816e9251ca191c3d6","tags":"","description":"This is a mock token for testing","totalSupply":"0.01","website":"https://www.baidu.com","tg":"https://www.baidu.com","x":"https://www.baidu.com","fee":"0.01","createdBy":"0xb492192a8793ec8c2c00379a6de6c9dac8f3bc91"}' \
http://127.0.0.1:8080/token/create


curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"Test bas","symbol":"AIJ","image":"http://gips3.baidu.com/it/u=119870705,2790914505&fm=3028&app=3028&f=JPEG&fmt=auto?w=1280&h=720","contract":"0xc6723a6a9a9ac90191aa257ccecfa969ccd2017cc36ca57e4f1626f0f082b028","tags":"","description":"This is a mock token for testing","totalSupply":"$0.0","website":"https://www.baidu.com","tg":"https://www.baidu.com","x":"https://www.baidu.com","Fee":"0.02","InitialBuy":1,"createdBy":"0xc8f7b5d8e1cca8475a9677afde15840c70d77190"}' \
  http://127.0.0.1:8080/token/create

``` 
* response
``` json
{
  "code": 0,
  "data": null,
  "lang": "en",
  "msg": "success"
}
```

### list token
* request
``` shell
curl -X GET -H "Content-Type: application/json" "http://127.0.0.1:8080/token/list"
```
* response
``` json
{
  "code": 0,
  "data": [
    {
      "aonFee": "0.000000000000000000",
      "contract": "0x9785a2919f53d9202aad77664a72ab8ef20e3536",
      "creator": "0xc8f7b5d8e1cca8475a9677afde15840c70d77190",
      "holderCnt": 2,
      "listed": false,
      "name": "TestAI",
      "price": "0.000000001600000000",
      "symbol": "asdddd"
    },
    {
      "aonFee": "0.000000000000000000",
      "contract": "0xa8594cf01460461eae795f22531faa3304e78040",
      "creator": "0xc8f7b5d8e1cca8475a9677afde15840c70d77190",
      "holderCnt": 1,
      "listed": false,
      "name": "niaosd",
      "price": "0.000000001600000000",
      "symbol": "asdasd"
    },
    {
      "aonFee": "0.000000000000000000",
      "contract": "0x8c1a694cbd0ee7008708c8363e2dc9b25175cbba",
      "creator": "0xc8f7b5d8e1cca8475a9677afde15840c70d77190",
      "holderCnt": 1,
      "listed": false,
      "name": "asd",
      "price": "0.000000001600000000",
      "symbol": "zciqwowe"
    },
    {
      "aonFee": "0.000000000000000000",
      "contract": "0x2dec13fe9d00315bac31e934c56431e1af9aa002",
      "creator": "0xc8f7b5d8e1cca8475a9677afde15840c70d77190",
      "holderCnt": 1,
      "listed": false,
      "name": "jnnn",
      "price": "0.000000001600000000",
      "symbol": "qwezx"
    },
    {
      "aonFee": "0.000000000000000000",
      "contract": "0x40aeba8633f78221c01fde61887de0650be442c3",
      "creator": "0xc8f7b5d8e1cca8475a9677afde15840c70d77190",
      "holderCnt": 1,
      "listed": false,
      "name": "tesst2",
      "price": "0.000000001600000000",
      "symbol": "jasdasdddd"
    },
    {
      "aonFee": "0.000000000000000000",
      "contract": "0x6b3c1b3426353bbe19f84387e7bf1e6ea2f32b22",
      "creator": "0xc8f7b5d8e1cca8475a9677afde15840c70d77190",
      "holderCnt": 1,
      "listed": false,
      "name": "TestAnn",
      "price": "0.000000001600000000",
      "symbol": "lloqwe"
    },
    {
      "aonFee": "0.000000000000000000",
      "contract": "0xe5a6bbc4d564805febf9f2126effd60208502c39",
      "creator": "0xc8f7b5d8e1cca8475a9677afde15840c70d77190",
      "holderCnt": 2,
      "listed": false,
      "name": "testa",
      "price": "0.000000001600000000",
      "symbol": "asd123nnn"
    },
    {
      "aonFee": "0.000000000000000000",
      "contract": "0x2b44a2bae45db7c3621180ff907c8dd8d81410dc",
      "creator": "0xc8f7b5d8e1cca8475a9677afde15840c70d77190",
      "holderCnt": 2,
      "listed": false,
      "name": "TestAI",
      "price": "0.000000001600000000",
      "symbol": "asd"
    },
    {
      "aonFee": "0.000000000000000000",
      "contract": "0xcddb836886b5e3820f0fecb4fc6e7e7d4049893f",
      "creator": "0xc8f7b5d8e1cca8475a9677afde15840c70d77190",
      "holderCnt": 2,
      "listed": false,
      "name": "TestAI",
      "price": "0.000000001600000000",
      "symbol": "tscasdc1"
    },
    {
      "aonFee": "0.000000000000000000",
      "contract": "0x3fd0e22c898f2860bbb5c3e3a8e3e20a203822ca",
      "creator": "0xc8f7b5d8e1cca8475a9677afde15840c70d77190",
      "holderCnt": 2,
      "listed": false,
      "name": "TestAI",
      "price": "0.000000001600000000",
      "symbol": "tscddc1"
    }
  ],
  "lang": "en",
  "msg": "success"
}
```

### top holer
* request
``` shell
curl -X GET -H "Content-Type: application/json" "http://127.0.0.1:8080/token/holder?token=0x54791a2d86e73b5f24c7921816e9251ca191c3d3"
``` 

* response
``` json
{
  "code": 0,
  "data": [
    {
      "amount": "999824422.789556700000000000",
      "holder": "0x54791a2d86e73b5f24c7921816e9251ca191c3d3",
      "id": "0x54791a2d86e73b5f24c7921816e9251ca191c3d30x54791a2d86e73b5f24c7921816e9251ca191c3d3"
    },
    {
      "amount": "51858.475547085610000000",
      "holder": "0x76b713f30734450ce566c170fda27e8dce63b1f6",
      "id": "0x76b713f30734450ce566c170fda27e8dce63b1f60x54791a2d86e73b5f24c7921816e9251ca191c3d3"
    },
    {
      "amount": "61869.490977180925000000",
      "holder": "0xb492192a8793ec8c2c00379a6de6c9dac8f3bc91",
      "id": "0xb492192a8793ec8c2c00379a6de6c9dac8f3bc910x54791a2d86e73b5f24c7921816e9251ca191c3d3"
    },
    {
      "amount": "61849.243919022900000000",
      "holder": "0xc8f7b5d8e1cca8475a9677afde15840c70d77190",
      "id": "0xc8f7b5d8e1cca8475a9677afde15840c70d771900x54791a2d86e73b5f24c7921816e9251ca191c3d3"
    }
  ],
  "lang": "en",
  "msg": "success"
}
```


### 24h trade digest
* request
``` shell
curl -X GET -H "Content-Type: application/json" "http://127.0.0.1:8080/digest/24h?token=0x54791a2d86e73b5f24c7921816e9251ca191c3d3"
``` 
* response
``` json
{
  "code": 0,
  "data": {
    "change": "0.000000000000000000",
    "percentage": "0.000000000000000000",
    "price": "0.000000001682880000",
    "volume": "0.000000000000000000"
  },
  "lang": "en",
  "msg": "success"
}
```

### current eth price
* request
``` shell
curl -X GET -H "Content-Type: application/json" "http://127.0.0.1:8080/digest/ethPrice"
```

* response
``` json
{
  "code": 0,
  "data": "3231.690000000000000000",
  "lang": "en",
  "msg": "success"
}
```