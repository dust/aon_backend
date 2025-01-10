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

