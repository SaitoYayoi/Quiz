import streamlit as st
import json
import random
import time

# 1. 页面基础配置：设为宽屏模式
st.set_page_config(page_title="医考刷题王", layout="wide", initial_sidebar_state="collapsed")

# 2. 注入自定义 CSS 样式：打造圆形按钮和美化界面
st.markdown("""
    <style>
    /* 强行修改按钮为圆形 */
    div.stButton > button {
        border-radius: 50% !important;
        width: 35px !important;
        height: 35px !important;
        padding: 0px !important;
        line-height: 35px !important;
        display: inline-block !important;
        margin: 2px !important;
        border: none !important;
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.1);
        border: 1px solid #4B8BBE !important;
    }
    /* 去掉侧边栏顶部的多余间距 */
    .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# 3. 初始化全局状态
if 'all_questions' not in st.session_state:
    st.session_state.all_questions = []
if 'shuffled_indices' not in st.session_state:
    st.session_state.shuffled_indices = []
if 'current_idx_in_list' not in st.session_state:
    st.session_state.current_idx_in_list = 0
if 'results' not in st.session_state:
    st.session_state.results = {} # 存储格式 {题目ID: "correct" | "incorrect"}
if 'error_mode' not in st.session_state:
    st.session_state.error_mode = False
if 'last_sub' not in st.session_state:
    st.session_state.last_sub = ""

# --- 4. 左侧侧边栏：清爽控制台 ---
with st.sidebar:
    st.title("⚙️ 练习设置")
    subject_map = {
        "临床检验基础": "linjian.json",
        "待添加学科2": "subject2.json"
    }
    selected_sub_name = st.selectbox("当前学科", list(subject_map.keys()))
    
    # 统计指标
    st.divider()
    correct_count = list(st.session_state.results.values()).count("correct")
    incorrect_count = list(st.session_state.results.values()).count("incorrect")
    total_q = len(st.session_state.all_questions)
    
    if total_q > 0:
        st.metric("正确数", f"{correct_count}")
        st.metric("错误数", f"{incorrect_count}")
        accuracy = (correct_count / (correct_count + incorrect_count) * 100) if (correct_count + incorrect_count) > 0 else 0
        st.write(f"📊 正确率：**{accuracy:.1f}%**")
        
        if st.button("🔄 重置进度"):
            st.session_state.last_sub = ""
            st.rerun()

# --- 5. 学科数据加载逻辑 ---
if selected_sub_name != st.session_state.last_sub:
    data = load_data(subject_map[selected_sub_name])
    if data:
        st.session_state.all_questions = data
        indices = list(range(len(data)))
        random.shuffle(indices)
        st.session_state.shuffled_indices = indices
        st.session_state.current_idx_in_list = 0
        st.session_state.results = {}
        st.session_state.last_sub = selected_sub_name
        st.session_state.error_mode = False

# --- 6. 主界面布局：左侧答题，右侧看板 ---
main_col, board_col = st.columns([0.75, 0.25])

with main_col:
    if not st.session_state.all_questions:
        st.info("👋 欢迎使用刷题宝！请确保您的 JSON 数据文件已上传。")
    elif st.session_state.current_idx_in_list >= len(st.session_state.all_questions):
        st.balloons()
        st.success("🏆 全题库通关！点击左侧重置进度可重新开始。")
    else:
        # 当前题目逻辑
        cur_list_idx = st.session_state.current_idx_in_list
        actual_q_idx = st.session_state.shuffled_indices[cur_list_idx]
        q = st.session_state.all_questions[actual_q_idx]

        st.subheader(f"📖 {selected_sub_name}")
        st.caption(f"随机序列：{cur_list_idx + 1} / {total_q} （原始题号：{actual_q_idx + 1}）")
        st.divider()
        
        st.markdown(f"#### {q['question']}")
        
        # 选项显示
        user_choice = st.radio(
            "请选择你的答案：", 
            q['options'], 
            index=None, 
            key=f"active_q_{actual_q_idx}",
            disabled=st.session_state.error_mode
        )
    
        # 自动判断逻辑
        if user_choice and not st.session_state.error_mode:
            correct_letter = q['answer'].strip().upper()
            if user_choice.startswith(correct_letter):
                st.session_state.results[actual_q_idx] = "correct"
                st.success("✅ 正确！即将进入下一题...")
                time.sleep(0.7)
                st.session_state.current_idx_in_list += 1
                st.rerun()
            else:
                st.session_state.results[actual_q_idx] = "incorrect"
                st.session_state.error_mode = True
                st.rerun()
    
        # 错误展示
        if st.session_state.error_mode:
            st.error(f"❌ 答错了！正确答案是：**{q['answer']}**")
            if st.button("下一题 ➔", type="primary"):
                st.session_state.error_mode = False
                st.session_state.current_idx_in_list += 1
                st.rerun()

with board_col:
    # 右侧折叠看板
    with st.expander("📍 题目看板 (点击跳转)", expanded=True):
        st.write("点击圆圈可直接跳转到指定题目：")
        # 创建网格
        grid_cols = st.columns(4) 
        for i in range(total_q):
            status = st.session_state.results.get(i)
            # 根据状态设置不同的 Emoji 颜色提示（CSS 注入无法区分单个按钮颜色，故用样式模拟）
            # 我们通过 markdown + 按钮组合，或者简单的 Emoji 方案
            
            # 颜色逻辑：
            # 由于 Streamlit button 限制，我们使用 CSS 背景颜色来区分
            # 下面是技巧：通过 st.markdown 生成自定义样式的按钮
            
            if status == "correct":
                # 正确显示为绿色背景按钮的模拟
                color = "#28a745" # 绿
                text_color = "white"
            elif status == "incorrect":
                color = "#dc3545" # 红
                text_color = "white"
            else:
                color = "#f0f2f6" # 灰
                text_color = "#333"
    
            # 注入单个按钮的颜色（此法较为高级，利用 key 进行选择性注入）
            st.markdown(f"""
                <style>
                div.stButton > button[key="btn_{i}"] {{
                    background-color: {color} !important;
                    color: {text_color} !important;
                }}
                </style>
            """, unsafe_allow_html=True)
            
            if grid_cols[i % 4].button(f"{i+1}", key=f"btn_{i}"):
                # 寻找该题在洗牌序列中的位置
                try:
                    st.session_state.current_idx_in_list = st.session_state.shuffled_indices.index(i)
                    st.session_state.error_mode = False
                    st.rerun()
                except ValueError:
                    pass