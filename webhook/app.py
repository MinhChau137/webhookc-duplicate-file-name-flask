from flask import Flask, request, render_template
from minio import Minio
from minio.error import S3Error

app = Flask(__name__)

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadminpassword",
    secure=False
)

def check_file_exists(bucket_name, file_name):
    try:
        client.stat_object(bucket_name, file_name)
        return True
    except S3Error as exc:
        if exc.code == "NoSuchKey":
            return False
        else:
            print("Error:", exc)
            return None

def upload_file(bucket_name, file_name, file_path):
    try:
        client.fput_object(bucket_name, file_name, file_path)
        print(f"File '{file_name}' uploaded successfully to bucket '{bucket_name}'.")
    except S3Error as exc:
        print(f"Error uploading file '{file_name}':", exc)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        bucket_name = request.form['bucket_name']  # Lấy tên bucket từ người dùng
        file_name = file.filename
        file_path = f"/tmp/{file_name}"
        file.save(file_path)

        # Kiểm tra sự tồn tại của file trong bucket
        if check_file_exists(bucket_name, file_name):
            return render_template('index.html', message=f"File '{file_name}' đã tồn tại trong bucket '{bucket_name}'. Bạn có muốn upload đè không?", file_name=file_name, file_path=file_path, bucket_name=bucket_name)
        else:
            upload_file(bucket_name, file_name, file_path)
            return render_template('index.html', message=f"File '{file_name}' đã được upload thành công vào bucket '{bucket_name}'.")
    
    return render_template('index.html')

@app.route('/confirm_upload', methods=['POST'])
def confirm_upload():
    file_name = request.form['file_name']
    file_path = request.form['file_path']
    bucket_name = request.form['bucket_name']  # Lấy bucket name từ request
    upload_file(bucket_name, file_name, file_path)
    return render_template('index.html', message=f"File '{file_name}' đã được upload thành công vào bucket '{bucket_name}'.")

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
