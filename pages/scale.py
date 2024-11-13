import streamlit as st
import subprocess
import json
import time


def get_blog_containers():
    try:
        # 'blog'가 이름에 포함된 모든 컨테이너 목록 가져오기
        container_names = (
            subprocess.check_output(
                ["docker", "ps", "--filter", "name=blog", "--format", "{{.Names}}"]
            )
            .decode("utf-8")
            .splitlines()
        )

        if not container_names:
            print("No containers with 'blog' in their name are currently running.")
        return container_names

    except subprocess.CalledProcessError as e:
        print("Error fetching container list:", e)
        return []


def get_container_stats(container_name):
    try:
        # 각 컨테이너의 stats 정보를 가져오기
        result = subprocess.check_output(
            ["docker", "stats", container_name, "--no-stream", "--format", "{{json .}}"]
        )
        stats = json.loads(result.decode("utf-8"))
        return float(stats["CPUPerc"].replace("%", ""))

    except subprocess.CalledProcessError as e:
        print(f"Error fetching stats for container {container_name}:", e)
        return None


def get_average_cpu_usage():
    container_names = get_blog_containers()
    if not container_names:
        return {}, None  # return empty dictionary and None for average

    cpu_usages = {}
    for name in container_names:
        cpu_usage = get_container_stats(name)
        if cpu_usage is not None:
            cpu_usages[name] = cpu_usage

    # CPU 사용량이 있는 경우 평균 계산
    if cpu_usages:
        average_cpu = sum(cpu_usages.values()) / len(cpu_usages)
        return cpu_usages, average_cpu
    else:
        return {}, None  # return empty dictionary and None


def scale_out_blog_containers():
    # 현재 'blog' 컨테이너 수 확인
    container_names = get_blog_containers()
    current_count = len(container_names)

    # Scale out 실행
    subprocess.run(
        ["docker", "compose", "up", "-d", "--scale", f"blog={current_count + 1}"]
    )


def scale_in_blog_containers():
    # 현재 'blog' 컨테이너 수 확인
    container_names = get_blog_containers()
    current_count = len(container_names)

    if current_count > 1:  # 최소 1개의 인스턴스가 남아야 하므로
        print("CPU usage below 0.3%. Scaling in...")
        subprocess.run(
            ["docker", "compose", "up", "-d", "--scale", f"blog={current_count - 1}"]
        )
        print("Scaled in: Reduced the number of blog instances.")


# Streamlit 인터페이스
st.title("CPU Usage Monitoring and Scaling")

# CPU 사용률 주기적 업데이트
cpu_usages, average_cpu_usage = get_average_cpu_usage()

# Check if CPU usages and average CPU usage are valid
if cpu_usages and average_cpu_usage is not None:
    # CPU 사용률 표시
    st.metric(label="Average CPU Usage (%)", value=f"{average_cpu_usage:.2f}")

    st.subheader("Individual Container CPU Usage")
    st.bar_chart(cpu_usages)

    # 스케일 아웃 버튼
    with st.container():
        l, r = st.columns([1, 1])
        if l.button("Scale Out", use_container_width=True):
            scale_out_blog_containers()
            st.rerun()

        # 스케일 인 버튼
        if r.button("Scale In", use_container_width=True):
            scale_in_blog_containers()
            st.rerun()
else:
    st.write("No CPU usage data available or no containers are running.")

# 일정 간격으로 페이지 갱신
time.sleep(10)
st.rerun()
