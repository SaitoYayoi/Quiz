import streamlit as st
import json
import random
import time

# 页面基础设置
st.set_page_config(page_title="医学刷题宝-视觉优化版", layout="centered")

# --- 新增：仅针对字体和间距的视觉微调 ---
st.markdown("""
    <style>
    /* 1. 调大题目文字字体 */
    .stMarkdown h4 {
        font-size: 22px !important;
        line-height: 1.5 !important;
    }
    /* 2. 调大选项 (Radio) 的文字字体 */
    div[data-testid="stMarkdownContainer"] p {
        font-size: 19px !important;
    }
    /* 3. 增大选项之间的行间距（上下间距）*/
    [data-testid="stRadio"] label {
        margin-bottom: 12px !important;
        padding: 5px 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# --- 1. 初始化 Session State ---
if 'all_questions' not in st.session_state:
    st.session_state.all_questions = []
if 'shuffled_indices' not in st.session_state:
    st.session_state.shuffled_indices = []
if 'current_idx_in_list' not in st.session_state:
    st.session_state.current_idx_in_list = 0
if 'stats' not in st.session_state:
    st.session_state.stats = {"correct": 0, "incorrect": 0}
if 'error_mode' not in st.session_state:
    st.session_state.error_mode = False
if 'last_sub' not in st.session_state:
    st.session_state.last_sub = ""

# --- 2. 侧边栏：设置与统计 ---
st.sidebar.title("📊 练习统计")

subject_map = {
    "临床检验基础": "linjian.json",
    "待添加学科2": "subject2.json"
}
selected_sub_name = st.sidebar.selectbox("切换学科模块", list(subject_map.keys()))

if selected_sub_name != st.session_state.last_sub:
    data = load_data(subject_map[selected_sub_name])
    if data:
        st.session_state.all_questions = data
        indices = list(range(len(data)))
        random.shuffle(indices)
        st.session_state.shuffled_indices = indices
        st.session_state.current_idx_in_list = 0
        st.session_state.stats = {"correct": 0, "incorrect": 0}
        st.session_state.last_sub = selected_sub_name
        st.session_state.error_mode = False

total_q = len(st.session_state.all_questions)
if total_q > 0:
    done_q = st.session_state.current_idx_in_list
    st.sidebar.write(f"练习进度：{done_q} / {total_q}")
    st.sidebar.progress(done_q / total_q)
    
    col1, col2 = st.sidebar.columns(2)
    col1.metric("正确", st.session_state.stats["correct"])
    col2.metric("错误", st.session_state.stats["incorrect"])
    
    total_answered = st.session_state.stats["correct"] + st.session_state.stats["incorrect"]
    accuracy = (st.session_state.stats["correct"] / total_answered * 100) if total_answered > 0 else 0
    st.sidebar.write(f"当前正确率：{accuracy:.1f}%")
    
    if st.sidebar.button("🔄 重新开始本科练习"):
        st.session_state.last_sub = ""
        st.rerun()

# --- 3. 主界面逻辑 ---
st.title(f"📖 {selected_sub_name}")

if not st.session_state.all_questions:
    st.warning("⚠️ 未检测到有效题库。")
elif st.session_state.current_idx_in_list >= total_q:
    st.balloons()
    st.success("🎉 太棒了！你已经完成了本学科的所有题目！")
    st.write(f"最终正确率：{accuracy:.1f}%")
else:
    actual_idx = st.session_state.shuffled_indices[st.session_state.current_idx_in_list]
    q = st.session_state.all_questions[actual_idx]
    
    st.divider()
    st.markdown(f"**随机序列：{st.session_state.current_idx_in_list + 1} / {total_q}** (原题号: {actual_idx + 1})")
    st.markdown(f"#### {q['question']}")
    
    user_choice = st.radio(
        "请选择答案：", 
        q['options'], 
        index=None, 
        key=f"q_{actual_idx}",
        disabled=st.session_state.error_mode
    )
    
    if user_choice and not st.session_state.error_mode:
        correct_letter = q['answer'].strip().upper()
        if user_choice.startswith(correct_letter):
            st.session_state.stats["correct"] += 1
            st.success("✅ 回答正确！")
            time.sleep(0.4)
            st.session_state.current_idx_in_list += 1
            st.rerun()
        else:
            st.session_state.stats["incorrect"] += 1
            st.session_state.error_mode = True
            st.rerun()
    
    if st.session_state.error_mode:
        st.error(f"❌ 答错了！正确答案是：**{q['answer']}**")
        if st.button("下一题 ➔", type="primary"):
            st.session_state.error_mode = False
            st.session_state.current_idx_in_list += 1
            st.rerun()