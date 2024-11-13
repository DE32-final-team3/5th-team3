import time
import mysql.connector
from prometheus_client import start_http_server, Counter, Gauge
import random

# MySQL 데이터베이스 연결 정보
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'exporter'
DB_PASSWORD = 'abcd1234'
DB_NAME = 'mysql'

# Prometheus 메트릭 정의
query_counter = Counter('mysql_query_total', 'Total number of queries executed')
query_duration_histogram = Gauge('mysql_query_duration_seconds', 'Query execution time in seconds')
db_status_gauge = Gauge('mysql_db_status', 'Database status (1 for active, 0 for inactive)')

# MySQL에 연결하는 함수
def get_mysql_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# 메트릭 수집 함수
def collect_metrics():
    connection = get_mysql_connection()
    cursor = connection.cursor()

    try:
        # 쿼리 실행 시간 측정 (예: `SHOW STATUS` 쿼리)
        start_time = time.time()
        cursor.execute("SHOW STATUS LIKE 'Cpu%';")  # 예시 쿼리: 현재 연결된 스레드 수 확인
        query_duration = time.time() - start_time
        
        # 쿼리 실행 메트릭 업데이트
        query_counter.inc()  # 쿼리 실행 카운트 증가
        query_duration_histogram.set(query_duration)  # 쿼리 실행 시간 설정

        # 데이터베이스 상태를 1로 설정 (활성화된 상태)
        db_status_gauge.set(1)
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db_status_gauge.set(0)  # 연결 실패 시 데이터베이스 상태를 0으로 설정 (비활성화 상태)
        
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    # Prometheus HTTP 서버 시작 (기본 포트 8000)
    start_http_server(8000)

    # 메트릭 수집을 5초마다 반복
    while True:
        collect_metrics()
        time.sleep(5)  # 5초 간격으로 메트릭 수집

