import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

# Prometheus에서 메트릭 데이터를 가져오는 함수
def fetch_prometheus_metrics():
    url = 'http://localhost:8000/metrics'  # Prometheus /metrics 엔드포인트
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"Failed to fetch metrics, Status Code: {response.status_code}"
    except Exception as e:
        return f"Error fetching metrics: {e}"

# 메트릭 데이터를 파싱하는 함수
def parse_metrics(metrics):
    lines = metrics.split("\n")
    data = {
        'metric': [],
        'value': []
    }

    for line in lines:
        if line.startswith("#"):
            continue  # 주석은 무시
        if line.strip() != "":
            parts = line.split(" ")
            if len(parts) >= 2:
                metric_name = parts[0]
                try:
                    metric_value = float(parts[1])  # 숫자 변환 시 예외 처리
                    data['metric'].append(metric_name)
                    data['value'].append(metric_value)
                except ValueError:
                    continue  # 숫자 변환 실패 시 건너뛰기
    return pd.DataFrame(data)

# 그래프 생성 함수
def generate_chart(df):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # 첫 번째 축 (CPU 사용률, myapp_requests_total)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Value (CPU Usage and Requests)", color='tab:blue')

    # 'myapp_cpu_usage' 메트릭 데이터만 필터링
    cpu_data = df[df['metric'].str.contains('myapp_cpu_usage')]
    ax1.plot(cpu_data['timestamp'], cpu_data['value'], label="CPU Usage (%)", color='tab:blue')

    # 'myapp_requests_total' 메트릭 데이터만 필터링
    requests_data = df[df['metric'].str.contains('myapp_requests_total')]
    ax1.plot(requests_data['timestamp'], requests_data['value'], label="Requests Total", color='tab:green')

    # 축 색상 맞추기
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # 두 번째 축 (process_virtual_memory_bytes)
    ax2 = ax1.twinx()
    ax2.set_ylabel("Virtual Memory (Bytes)", color='tab:red')

    # 'process_virtual_memory_bytes' 메트릭 데이터만 필터링
    memory_data = df[df['metric'].str.contains('process_virtual_memory_bytes')]
    ax2.plot(memory_data['timestamp'], memory_data['value'], label="Virtual Memory (Bytes)", color='tab:red')

    # 축 색상 맞추기
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # 제목, 레이블, 범례 추가
    ax1.set_title("Prometheus Metrics - CPU Usage, Requests Total, Virtual Memory")
    fig.tight_layout()  # 레이아웃 조정
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    return fig

# Streamlit 애플리케이션
def main():
    st.title("Prometheus Metrics Visualization")

    # 데이터 저장을 위한 DataFrame 초기화
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame(columns=['metric', 'value', 'timestamp'])
        st.session_state.cumulative_data = {
            'myapp_requests_total': 0,
            'process_virtual_memory_bytes': 0,
            'myapp_cpu_usage': 0
        }

    # 1분마다 데이터를 갱신하여 가져오고 그래프를 업데이트
    chart_placeholder = st.empty()  # 차트를 출력할 자리

    while True:
        # Prometheus에서 메트릭을 가져옵니다.
        metrics = fetch_prometheus_metrics()

        # 메트릭을 데이터프레임으로 파싱
        df = parse_metrics(metrics)

        # 현재 시간 추가 (시간 추적용)
        df['timestamp'] = pd.to_datetime('now')

        # 누적 값 계산: 각 메트릭을 누적하여 저장
        for i, row in df.iterrows():
            metric_name = row['metric']
            if metric_name in st.session_state.cumulative_data:
                # 누적 값에 더하기
                st.session_state.cumulative_data[metric_name] += row['value']
                row['value'] = st.session_state.cumulative_data[metric_name]

        # 새로운 데이터를 세션 상태에 누적
        st.session_state.data = pd.concat([st.session_state.data, df], ignore_index=True)

        # 차트 갱신
        chart_placeholder.pyplot(generate_chart(st.session_state.data))

main()

# 1분마다 갱신 (60초 대기)
time.sleep(60)  # 1분 간격으로 데이터를 갱신
st.rerun()  # 앱을 강제로 다시 실행하여 갱신
