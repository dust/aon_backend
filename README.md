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

