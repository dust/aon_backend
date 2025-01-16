import os
import secrets
from flask import Blueprint, request, current_app

from werkzeug.utils import secure_filename
from aon.response import ResMsg, ResponseCode


upload_router = Blueprint("upload", __name__, url_prefix='/upload')


@upload_router.route("/image", methods=["POST"])
def upload_image():
    if 'file' not in request.files:
        print("xxxx")
        res = ResMsg()
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
    file = request.files['file']
    if file.filename == '':
        print("xxxx2")
        res = ResMsg()
        res.update(code=ResponseCode.InvalidParameter)
        return res
    print("filename:", file.filename.lower())
    if file and file.filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
        try:
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(file.filename)
            filename = random_hex + f_ext
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            # 确保上传目录存在
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)

            # 构建文件URL
            file_url = current_app.config['UPLOAD_FILE_URL'] + filename
            res = ResMsg(data=file_url)
            return res.data
        except Exception as e:
            import traceback
            traceback.print_exception(e)
            res = ResMsg()
            res.update(code=ResponseCode.SystemError)
            return res.data
    else:
        print("xxxx3")
        res = ResMsg()
        res.update(code=ResponseCode.InvalidParameter)
        return res.data
