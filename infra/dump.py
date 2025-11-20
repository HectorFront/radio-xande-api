import os
import boto3
import threading
import subprocess
from infra.environments import env

class DumpSQL:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_stop_event"):
            self._stop_event = threading.Event()
            self._dump_sql_thread = None

    def start(self):
        with self._lock:
            if self._dump_sql_thread is None or not self._dump_sql_thread.is_alive():
                self._dump_sql_thread = threading.Thread(target=self.schedule_dump, daemon=True)
                self._dump_sql_thread.start()

    def stop(self):
        if self._dump_sql_thread and self._dump_sql_thread.is_alive():
            self._stop_event.set()
            self._dump_sql_thread.join()

    @staticmethod
    def dump():
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=env.get('S3_ACCESS_KEY'),
                aws_secret_access_key=env.get('S3_SECRET_ACCESS_KEY'),
                endpoint_url=env.get('S3_ENDPOINT_URL')
            )
            s3_key = "backup.sql"
            current_path = os.path.dirname(os.path.abspath(__file__))
            backup_path = os.path.join(current_path, '..', 'backup', 'sql')
            os.makedirs(backup_path, exist_ok=True)
            dump_path = os.path.join(backup_path, s3_key)
            dump_command = f"mysqldump -u {env.get('USER_MYSQL_PROD')} -p{env.get('PASSWORD_MYSQL_PROD')} {env.get('DATABASE_MYSQL_PROD')} > {dump_path}"
            process = subprocess.run(dump_command, shell=True, check=True, capture_output=True, text=True)
            if process.returncode != 0:
                raise Exception(f"mysqldump failed with return code {process.returncode}\nError: {process.stderr}")
            bucket_name = env.get('S3_BUCKET_NAME_BACKUP')
            s3.upload_file(dump_path, bucket_name, s3_key)
            print(f"Upload completed successfully to S3: {s3_key}")
        except subprocess.CalledProcessError as err:
            print(f"mysqldump failed with error:\n{err.stderr}")
        except Exception as err:
            print(f"Unexpected error: {err}")

    def schedule_dump(self):
        interval_24_hours = 24 * 3600
        while not self._stop_event.is_set():
            self.dump()
            self._stop_event.wait(interval_24_hours)