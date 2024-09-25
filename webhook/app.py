from flask import Flask, request
from flask_socketio import SocketIO
from minio import Minio
from minio.error import S3Error

app = Flask(__name__)
socketio = SocketIO(app)

# Khởi tạo client MinIO
minio_client = Minio(
    "localhost:9000",  # Địa chỉ MinIO
    access_key="minioadmin",
    secret_key="minioadminpassword",
    secure=False
)

@app.route('/notify', methods=['POST'])
def notify():
    data = request.json
    if 'Records' in data:
        for record in data['Records']:
            if record['eventName'] == 'PutObject':
                file_name = record['s3']['object']['key']
                if check_if_file_exists(record['s3']['bucket']['name'], file_name):
                    socketio.emit('file_duplicate', {'file_name': file_name})
    return '', 200

def check_if_file_exists(bucket_name, file_name):
    try:
        # Kiểm tra file đã tồn tại bằng cách lấy thông tin đối tượng
        minio_client.stat_object(bucket_name, file_name)
        return True  # File tồn tại
    except S3Error as e:
        if e.code == 'NoSuchKey':
            return False  # File không tồn tại
        raise  # Bỏ qua các lỗi khác

if __name__ == '__main__':
    socketio.run(host='0.0.0.0', port=5000)
