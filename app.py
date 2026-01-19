    import streamlit as st
    import json
    import random
    import time
    
    # 页面基础设置
    st.set_page_config(page_title="医学生专用刷题宝", layout="centered")
    
    def load_data(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    # --- 初始化状态 ---
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_q' not in st.session_state:
        st.session_state.current_q = None
    if 'last_sub' not in st.session_state:
        st.session_state.last_sub = ""
    if 'error_mode' not in st.session_state:
        st.session_state.error_mode = False
    
    # --- 侧边栏 ---
    st.sidebar.title("📚 学科模块")
    subject_map = {
        "临床检验基础": "linjian.json",
        "学科2": "subject2.json",
        "学科3": "subject3.json"
    }
    selected_sub_name = st.sidebar.selectbox("切换学科", list(subject_map.keys()))
    
    # 切换学科逻辑
    if selected_sub_name != st.session_state.last_sub:
        st.session_state.questions = load_data(subject_map[selected_sub_name])
        if st.session_state.questions:
            st.session_state.current_q = random.choice(st.session_state.questions)
        st.session_state.last_sub = selected_sub_name
        st.session_state.error_mode = False
    
    # --- 主界面 ---
    st.title(f"📖 {selected_sub_name}")
    
    if not st.session_state.questions:
        st.warning("尚未检测到题库文件，请确保 linjian.json 格式正确并已上传。")
    else:
        q = st.session_state.current_q
        
        st.divider()
        st.markdown(f"**第 {q['id']} 题**")
        st.markdown(f"#### {q['question']}")
    
        # 如果处于错误显示模式，禁用 radio 防止二次触发
        is_disabled = st.session_state.error_mode
    
        # 关键改动：使用 index=None 且移除提交按钮
        user_choice = st.radio(
            "请选择答案：", 
            q['options'], 
            index=None, 
            key=f"q_{q['id']}", # 每题唯一的 key 确保重置
            disabled=is_disabled
        )
    
        # --- 自动判断逻辑 ---
        if user_choice and not st.session_state.error_mode:
            correct_letter = q['answer'].strip().upper()
            
            if user_choice.startswith(correct_letter):
                # 1. 答对了：直接显示成功并瞬间跳转
                st.success("✅ 正确！自动进入下一题...")
                time.sleep(0.6) # 给 0.6 秒时间让眼睛确认一下绿色
                st.session_state.current_q = random.choice(st.session_state.questions)
                st.rerun()
            else:
                # 2. 答错了：进入错误模式，显示答案
                st.session_state.error_mode = True
                st.rerun()
    
        # --- 错误拦截界面 ---
        if st.session_state.error_mode:
            st.error(f"❌ 答错了！正确答案是：**{q['answer']}**")
            st.info("查看题目纠错后，点击下方按钮继续。")
            if st.button("下一题 ➔"):
                st.session_state.error_mode = False
                st.session_state.current_q = random.choice(st.session_state.questions)
                st.rerun()
    
        # 底部进度
        st.sidebar.metric("题库总量", len(st.session_state.questions))xxxxxxxxxx st.divider()st.subheader(f"第 {q['id']} 题")st.write(q['question'])# 选项显示# 使用 key 来确保每次换题时单选框重置user_choice = st.radio(    "选择你的答案：",     q['options'],     index=None,     key=f"radio_{q['id']}")# 提交按钮if st.button("提交回答", type="primary"):    if user_choice:        correct_letter = q['answer'].strip().upper()        if user_choice.startswith(correct_letter):            # --- 情况1：选择正确 ---            st.success("✅ 回答正确！正在进入下一题...")            time.sleep(0.8)  # 短暂延迟，让你看清正确提示            # 随机换下一题            st.session_state.current_q = random.choice(st.session_state.questions)            st.session_state.show_error = False            st.rerun()        else:            # --- 情况2：选择错误 ---            st.session_state.show_error = True    else:        st.warning("请先选择一个选项")# 错误反馈if st.session_state.show_error:    st.error(f"❌ 答错了。正确答案是：{q['answer']}")    st.info("你可以查看原题进行纠错，或者直接点击下方按钮跳过。")    if st.button("强制下一道"):        st.session_state.current_q = random.choice(st.session_state.questions)        st.session_state.show_error = False        st.rerun()# 进度提示st.sidebar.divider()st.sidebar.write(f"当前题库总数：{len(st.session_state.questions)}")