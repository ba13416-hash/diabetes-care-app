import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. 노인 친화적 화면 디자인 (CSS) 적용
# ==========================================
st.set_page_config(page_title="당뇨 건강 돌봄", page_icon="🍎", layout="wide")

custom_css = """
<style>
    html, body, [class*="css"]  {
        font-size: 22px !important; 
        font-family: 'Malgun Gothic', sans-serif;
    }
    h1 { font-size: 36px !important; color: #2C3E50; font-weight: 800; }
    h2 { font-size: 30px !important; color: #34495E; font-weight: 700; }
    h3 { font-size: 26px !important; color: #4A235A; font-weight: 600; }
    
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        font-size: 24px !important;
        font-weight: bold;
        height: 60px;
        width: 100%;
        border-radius: 15px;
        border: none;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        background-color: #45a049;
    }
    
    .stTextInput input, .stNumberInput input { font-size: 22px !important; }
    .stTabs [data-baseweb="tab-list"] button { font-size: 22px !important; }
    .stCheckbox label { font-size: 24px !important; padding-top: 10px; padding-bottom: 10px;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 2. 닉네임 기반 개별 데이터 저장소 설정
# ==========================================
# 사용자의 닉네임을 키(Key)로 하여 개별 데이터를 저장하는 딕셔너리 구조
if "app_data" not in st.session_state:
    st.session_state.app_data = {}

if "user" not in st.session_state:
    st.session_state.user = None

# ==========================================
# 3. 화면 UI 레이아웃 및 닉네임 로그인
# ==========================================
st.sidebar.title("🍎 당뇨 건강 돌봄")

if st.session_state.user is None:
    st.sidebar.subheader("접속하기")
    
    nickname = st.sidebar.text_input("사용하실 닉네임을 입력하세요", placeholder="예: 부산갈매기")
    demo_role = st.sidebar.radio("누구신가요?", ["👴 어르신 (사용자)", "👩‍⚕️ 복지사 선생님 (관리자)"])
    
    if st.sidebar.button("시작하기"):
        if nickname.strip() == "":
            st.sidebar.warning("닉네임을 반드시 입력해주세요.")
        else:
            # 어르신(사용자)으로 로그인 시 초기 데이터 구조 생성
            if demo_role == "👴 어르신 (사용자)":
                if nickname not in st.session_state.app_data:
                    st.session_state.app_data[nickname] = {
                        "checklists": [],
                        "hba1c_data": [],
                        "appointments": [],
                        "tasks": [
                            "💊 오늘 당뇨약을 드셨나요?",
                            "🚶‍♀️ 오늘 30분 이상 걸으셨나요?",
                            "🦶 발바닥에 상처가 없는지 확인하셨나요?"
                        ]
                    }
                st.session_state.user = {"nickname": nickname, "role": "patient"}
            else:
                # 관리자는 별도 닉네임으로 접속
                st.session_state.user = {"nickname": nickname, "role": "manager"}
            st.rerun()
else:
    st.sidebar.write(f"**{st.session_state.user['nickname']}** 님 반갑습니다!")
    if st.sidebar.button("종료하기(로그아웃)"):
        st.session_state.user = None
        st.rerun()

# ==========================================
# 4. 기능 화면
# ==========================================

# --- [A. 어르신 (이용자) 화면] ---
if st.session_state.user and st.session_state.user["role"] == "patient":
    st.title("📋 나의 건강 기록부")
    
    user_name = st.session_state.user["nickname"]
    user_data = st.session_state.app_data[user_name]
    
    tab1, tab2, tab3 = st.tabs(["오늘의 할 일", "혈당 점수(당화혈색소)", "할 일 추가하기"])
    
    # 1. 오늘의 할 일 및 병원 진료 일정
    with tab1:
        st.subheader("✅ 오늘 건강하게 보내셨나요?")
        today = datetime.now().strftime("%Y년 %m월 %d일")
        st.write(f"**날짜: {today}**")
        
        with st.form("checklist_form"):
            fasting_sugar = st.number_input("🩸 아침 식전 혈당 (목표: 100 근처)", min_value=0, max_value=500, value=100)
            post_sugar = st.number_input("🩸 식사 2시간 후 혈당 (목표: 140 근처)", min_value=0, max_value=500, value=140)
            
            st.markdown("---")
            st.write("**실천한 항목에 체크해 주세요.**")
            
            task_results = {}
            for task in user_data["tasks"]:
                task_results[task] = st.checkbox(task)
            
            notes = st.text_area("📝 오늘 컨디션은 어떠셨나요? (아픈 곳 등)")
            
            if st.form_submit_button("저장하기"):
                user_data["checklists"].append({
                    "date": today,
                    "fasting_sugar": fasting_sugar,
                    "post_sugar": post_sugar,
                    "tasks": task_results,
                    "notes": notes
                })
                st.success("🎉 참 잘하셨습니다! 오늘의 기록이 저장되었습니다.")

        st.markdown("---")
        st.subheader("🏥 병원 가는 날 (진료 일정)")
        
        # 일정 등록
        with st.form("appointment_form"):
            appt_date = st.date_input("진료 날짜를 선택하세요")
            appt_desc = st.text_input("어느 병원인지 적어주세요 (예: 보건소, 내과)")
            
            if st.form_submit_button("일정 달력에 추가하기"):
                if appt_desc:
                    user_data["appointments"].append({
                        "date": appt_date.strftime("%Y-%m-%d"),
                        "description": appt_desc
                    })
                    st.success("일정이 추가되었습니다.")
                else:
                    st.warning("병원 이름을 적어주세요.")
        
        # 일정 목록 확인
        if user_data["appointments"]:
            df_appt = pd.DataFrame(user_data["appointments"]).sort_values(by="date")
            df_appt.columns = ["예약 날짜", "진료 내용"]
            st.dataframe(df_appt, use_container_width=True, hide_index=True)
        else:
            st.info("예약된 진료 일정이 없습니다.")

    # 2. 당화혈색소 
    with tab2:
        st.subheader("📈 나의 3개월 평균 혈당 (당화혈색소)")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            with st.form("hba1c_form"):
                hba1c_val = st.number_input("수치 입력 (%)", min_value=3.0, max_value=20.0, step=0.1, value=6.5)
                test_date = st.date_input("병원 다녀온 날")
                
                if st.form_submit_button("기록하기"):
                    user_data["hba1c_data"].append({
                        "date": test_date.strftime("%Y-%m-%d"),
                        "value": hba1c_val
                    })
                    st.success("등록되었습니다.")
        
        with col2:
            if user_data["hba1c_data"]:
                df = pd.DataFrame(user_data["hba1c_data"]).sort_values(by="date")
                fig = px.line(df, x="date", y="value", title="내 혈당 점수 변화", markers=True)
                fig.add_hline(y=6.5, line_dash="dash", line_color="green", annotation_text="건강 목표선 (6.5%)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("아직 기록된 점수가 없습니다.")

    # 3. 목표 추가 기능 
    with tab3:
        st.subheader("💡 나만의 건강 목표 추가하기")
        
        recommendations = [
            "💧 하루에 물 6잔 이상 마시기",
            "🥗 식사할 때 채소 먼저 먹기",
            "🧦 외출할 때 반드시 양말 신기",
            "😴 밤 10시 이전에 잠자리에 들기"
        ]
        
        selected_rec = st.selectbox("추천 목표 중 선택하기", ["직접 입력하기"] + recommendations)
        custom_new_task = ""
        if selected_rec == "직접 입력하기":
            custom_new_task = st.text_input("새로운 목표를 직접 적어주세요.")
        
        if st.button("목표 추가하기"):
            new_task = custom_new_task if selected_rec == "직접 입력하기" else selected_rec
            if new_task and new_task not in user_data["tasks"]:
                user_data["tasks"].append(new_task)
                st.success(f"'{new_task}' 항목이 매일 할 일에 추가되었습니다!")
            elif new_task in user_data["tasks"]:
                st.warning("이미 추가된 목표입니다.")

# --- [B. 복지사 선생님 (관리자) 화면] ---
elif st.session_state.user and st.session_state.user["role"] == "manager":
    st.title("👩‍⚕️ 대상자 건강 모니터링 (관리자용)")
    
    patient_list = list(st.session_state.app_data.keys())
    
    if not patient_list:
        st.warning("현재 접속 기록이 있는 어르신 데이터가 없습니다.")
    else:
        selected_patient = st.selectbox("확인할 어르신을 선택하세요", patient_list)
        selected_data = st.session_state.app_data[selected_patient]
        
        st.divider()
        st.write(f"### 📌 [{selected_patient}] 어르신 건강 현황")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### 1. 일일 체크리스트 기록")
            if selected_data["checklists"]:
                display_data = []
                for record in selected_data["checklists"]:
                    row = {
                        "날짜": record["date"],
                        "식전 혈당": record["fasting_sugar"],
                        "식후 혈당": record["post_sugar"],
                        "목표 달성 수": sum(record["tasks"].values()),
                        "특이사항": record["notes"]
                    }
                    display_data.append(row)
                df_c = pd.DataFrame(display_data)
                st.dataframe(df_c, use_container_width=True)
            else:
                st.info("체크리스트 기록이 없습니다.")
                
            st.write("#### 3. 병원 진료 예약 일정")
            if selected_data["appointments"]:
                df_appt_m = pd.DataFrame(selected_data["appointments"]).sort_values(by="date")
                df_appt_m.columns = ["예약 날짜", "진료 내용"]
                st.dataframe(df_appt_m, use_container_width=True, hide_index=True)
            else:
                st.info("예약된 일정이 없습니다.")
                
        with col2:
            st.write("#### 2. 당화혈색소(HbA1c) 관리 현황")
            if selected_data["hba1c_data"]:
                df_h = pd.DataFrame(selected_data["hba1c_data"]).sort_values(by="date")
                fig = px.line(df_h, x="date", y="value", title=f"{selected_patient} 어르신 당화혈색소 추이", markers=True)
                fig.add_hline(y=6.5, line_dash="dash", line_color="red")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("기록된 데이터가 없습니다.")

elif st.session_state.user is None:
    st.info("왼쪽 사이드바에서 [시작하기]를 눌러주세요.")