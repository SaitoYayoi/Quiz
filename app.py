import streamlit as st
import json
import random
import time

# 页面基础设置
st.set_page_config(page_title="医学题库-全功能版", layout="wide")

# 自定义 CSS 样式：让侧边栏的题号网格更美观
st.markdown("""
    <style>
    .stButton>button { width: 100%; padding: 0px; height: 30px; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# --- 1. 初始化 Session State (核心存储) ---
if 'all_questions' not in st.session_state:
    st.session_state.all_questions = [] # 原始题目列表
if 'shuffled_indices' not in st.session_state:
    st.session_state.shuffled_indices = [] # 洗牌后的顺序
if 'current_idx_in_list' not in st.session_state:
    st.session_state.current_idx_in_list = 0 # 当前处于洗牌列表的第几个
if 'results' not in st.session_state:
    st.session_state.results = {} # 记录每道题状态：{原始索引: "correct" | "incorrect"}
if 'error_mode' not in st.session_state:
    st.session_state.error_mode = False
if 'last_sub' not in st.session_state:
    st.session_state.last_sub = ""

# --- 2. 侧边栏：学科选择与统计 ---
st.sidebar.title("🩺 学习控制台")

subject_map = {
    "临床检验基础": "linjian.json",
    "待添加学科2": "subject2.json"
}
selected_sub_name = st.sidebar.selectbox("选择学科", list(subject_map.keys()))

# 学科初始化/切换逻辑
if selected_sub_name != st.session_state.last_sub:
    data = load_data(subject_map[selected_sub_name])
    if data:
        st.session_state.all_questions = data
        indices = list(range(len(data)))
        random.shuffle(indices) # 初始随机洗牌
        st.session_state.shuffled_indices = indices
        st.session_state.current_idx_in_list = 0
        st.session_state.results = {}
        st.session_state.last_sub = selected_sub_name
        st.session_state.error_mode = False

# --- 3. 侧边栏：题号看板 (Question Map) ---
st.sidebar.divider()
st.sidebar.subheader("题号看板")

# 计算统计数据
correct_count = list(st.session_state.results.values()).count("correct")
incorrect_count = list(st.session_state.results.values()).count("incorrect")
total_q = len(st.session_state.all_questions)

# 绘制网格看板
if total_q > 0:
    # 进度条和指标
    st.sidebar.progress(len(st.session_state.results) / total_q)
    c1, c2 = st.sidebar.columns(2)
    c1.metric("正确", correct_count)
    c2.metric("错误", incorrect_count)

    # 题号按钮矩阵 (每行 5 个)
    cols = st.sidebar.columns(5)
    for i in range(total_q):
        # 确定这道题的状态和颜色
        btn_label = f"{i+1}"
        btn_key = f"map_btn_{i}"
        
        status = st.session_state.results.get(i)
        
        # Streamlit 按钮样式无法直接改颜色，我们通过前缀 Emoji 区分
        if status == "correct":
            display_label = f"✅{btn_label}"
        elif status == "incorrect":
            display_label = f"❌{btn_label}"
        else:
            display_label = f"⚪{btn_label}"
            
        # 点击题号跳转逻辑
        if cols[i % 5].button(display_label, key=btn_key):
            # 找到原始索引 i 在打乱列表中的位置，实现跳转
            st.session_state.current_idx_in_list = st.session_state.shuffled_indices.index(i)
            st.session_state.error_mode = False
            st.rerun()

# --- 4. 主界面：刷题逻辑 ---
st.title(f"📖 {selected_sub_name}")

if not st.session_state.all_questions:
    st.warning("⚠️ 请确保题库文件已正确放置并上传。")
elif st.session_state.current_idx_in_list >= total_q:
    st.balloons()
    st.success("🎊 恭喜！你已完成全部练习！")
    if st.button("重新开始"):
        st.session_state.last_sub = ""
        st.rerun()
else:
    # 获取当前题目
    actual_idx = st.session_state.shuffled_indices[st.session_state.current_idx_in_list]
    q = st.session_state.all_questions[actual_idx]
    
    st.divider()
    st.write(f"**当前位置：随机序列第 {st.session_state.current_idx_in_list + 1} 题 (原始题号: {actual_idx + 1})**")
    st.markdown(f"### {q['question']}")
    
    # 选项显示
    is_disabled = st.session_state.error_mode
    user_choice = st.radio(
        "选择答案：", 
        q['options'], 
        index=None, 
        key=f"active_q_{actual_idx}",
        disabled=is_disabled
    )
    
    # 判断逻辑
    if user_choice and not st.session_state.error_mode:
        correct_letter = q['answer'].strip().upper()
        
        if user_choice.startswith(correct_letter):
            st.session_state.results[actual_idx] = "correct"
            st.success("✅ 正确！自动进入下一题...")
            time.sleep(0.6)
            st.session_state.current_idx_in_list += 1
            st.rerun()
        else:
            st.session_state.results[actual_idx] = "incorrect"
            st.session_state.error_mode = True
            st.rerun()
    
    # 错误显示
    if st.session_state.error_mode:
        st.error(f"❌ 答错了！正确答案是：**{q['answer']}**")
        if st.button("查看下一题 ➔", type="primary"):
            st.session_state.error_mode = False
            st.session_state.current_idx_in_list += 1
            st.rerun()