from prometheus_client import Counter, Gauge, Histogram, Summary, start_http_server
import mysql.connector
import random
import time

# 카운터 메트릭: 요청 수
request_counter = Counter('myapp_requests_total', 'Total number of requests')

# 게이지  메트릭: CPU 사용률
cpu_usage = Gauge('myapp_cpu_usage', 'Current CPU usage percentage')

# 히스토그램 메트릭: 요청 처리 시간
request_duration_histogram = Histogram('myapp_request_duration_seconds', 'Request duration in seconds')

# 써머리 메트릭: 요청 처리 시간의 백분위수
request_duration_summary = Summary('myapp_request_duration_seconds_summary', 'Request duration summary')

# MySQL 연결 설정
db_config = {
    'host': 'localhost',
    'user': 'exporter',
    'password': 'abcd1234',
    'database': 'mysql',
    'charset': 'utf8mb4'
}
# MySQL에서 CPU 사용량을 조회하는 함수 (예시: `SHOW STATUS` 또는 `SHOW VARIABLES` 명령어)
def get_mysql_cpu_usage():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # 예시: SHOW STATUS에서 특정 정보를 가져오는 쿼리
        cursor.execute("SHOW STATUS LIKE 'Cpu%'")  # 실제 쿼리나 지표를 변경해야 할 수 있습니다.
        result = cursor.fetchone()
        if result:
            # 예시로 CPU 사용률을 100%로 가정
            cpu_usage_value = random.uniform(0, 100)  # 실제 값은 쿼리 결과에 맞게 수정
            return cpu_usage_value
        else:
            return 0
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return 0
    finally:
        cursor.close()
        connection.close()

# 요청 처리 함수
def process_request():
    # 요청 처리 시간 시뮬레이션
    start = time.time()
    time.sleep(random.uniform(0.5, 2.0))  # 요청을 처리하는 데 걸리는 시간 (0.5초 ~ 2초)
    duration = time.time() - start

    # 메트릭 업데이트
    request_counter.inc()  # 요청 수 증가
    request_duration_histogram.observe(duration)  # 히스토그램에 요청 처리 시간 기록
    request_duration_summary.observe(duration)  # 써머리에도 기록

    return duration

if __name__ == '__main__':
    # HTTP 서버 시작 (Prometheus가 /metrics 엔드포인트에서 메트릭을 수집)
    start_http_server(8000)

    # 메트릭을 5초마다 업데이트하는 예시
    while True:
        cpu_usage.set(get_mysql_cpu_usage())  # MySQL에서 가져온 CPU 사용률 업데이트
        process_request()  # 요청 처리 및 메트릭업데이트
        time.sleep(5)  # 5초마다 업데이트
