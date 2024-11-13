import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import subprocess
import time


def run_load_test(n, t):
    try:
        result = subprocess.run(
            [
                "ab",
                "-n",
                f"{n}",
                "-t",
                f"{t}",
                "http://localhost:9090/api/v1/query?query=up",
            ],
            capture_output=True,
            text=True,
        )
        return result.stdout
    except Exception as e:
        return f"Error running load test: {str(e)}"


# Prometheus API 설정
prometheus_url = "http://localhost:9090/api/v1/query_range"
step = "10"  # 샘플링 간격 (초 단위)

# Start 시간과 현재 시간(UTC)으로 설정된 End 시간
end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=12)

start_time = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
end_time = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

# CPU 코어 개수 설정 (예: 8개의 코어)
cpu_cores = 8

# 데이터 저장할 빈 DataFrame
all_data = pd.DataFrame()

# 각 CPU 코어에 대한 데이터 조회 및 데이터프레임에 저장
for i in range(cpu_cores):
    query = f'rate(node_cpu_seconds_total{{mode="user", cpu="{i}"}}[1m])'

    response = requests.get(
        prometheus_url,
        params={"query": query, "start": start_time, "end": end_time, "step": step},
    )

    data = response.json()

    if "data" in data and "result" in data["data"] and data["data"]["result"]:
        results = data["data"]["result"][0]["values"]
        df = pd.DataFrame(results, columns=["timestamp", f"cpu_{i}"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df[f"cpu_{i}"] = df[f"cpu_{i}"].astype(float)

        # 시간별로 데이터를 합치기 위해 timestamp를 기준으로 병합
        if all_data.empty:
            all_data = df
        else:
            all_data = pd.merge(all_data, df, on="timestamp", how="outer")

# Streamlit에서 데이터 출력 및 시각화
if not all_data.empty:
    # st.write(all_data)
    st.title("CPU Usage")
    st.line_chart(all_data.set_index("timestamp"))
else:
    st.write("No data returned from Prometheus.")

with st.container():
    p1, p2 = st.columns([1, 1])
    n = p1.number_input("전체 요청 수", step=10)
    t = p2.number_input("테스트 시간", step=10)

    if st.button("부하 테스트", use_container_width=True):
        result = run_load_test(n, t)
        st.text(result)  # 테스트 결과를 화면에 표시
