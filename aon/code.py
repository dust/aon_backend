class ResponseCode(object):
    Success = 0  # 成功
    Fail = -1  # 失败
    NoResourceFound = 40001  # 未找到资源
    InvalidParameter = 40002  # 参数无效
    AccountOrPassWordErr = 40003  # 账户或密码错误
    VerificationCodeError = 40004  # 验证码错误
    PleaseSignIn = 40005  # 请登陆
    InvalidOrExpired = 40006  # 验证码过期
    MobileNumberError = 40007  # 手机号错误
    FrequentOperation = 40008  # 操作频繁,请稍后再试
    SystemError = 40009  # 系统错误
    UserNameRepeat = 40010  # 用户名重复
    UserNameFormatError = 40011  # 用户名格式错误
    UploadError = 40012 # 上传错误

