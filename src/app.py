import streamlit as st
import sqlite3
import json
import requests

def call_llama(model, prompt, stream=False):
    url = 'http://localhost:11434/api/generate'
    data = {
        'model': model ,
        'prompt':prompt, 
        'stream': stream
    }

    json_data = json.dumps(data)
    response = requests.post(url, data=json_data, headers={'Content_Type': 'application/json'})
    if response.status_code == 200:
        return response.json()
    else:
        return f'Error: {response.status_code}'

conn = sqlite3.connect("School.db")

Curser = conn.cursor()

y = ''' CREATE TABLE IF NOT EXISTS students
(id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT, lname TEXT,
grade INTEGER)
'''

Curser.execute(y)

conn.commit()


# اتمام ساخت دیتابیس

operation = st.sidebar.selectbox("انتخاب عملیات", ["دیتابیس", "هوش مصنوعی"])

if operation == 'دیتابیس':
    crud = st.selectbox("یک عملیات را انتخاب کنید", ["ایجاد", "خواندن", "بروزرسانی", "حذف"])
    if crud == "ایجاد":
        st.title("ایجاد اطلاعات دانش آموز")
        name = st.text_input("نام دانش آموز")
        lname = st.text_input("نام خانوادگی دانش آموز")
        grade = st.number_input("معدل دانش آموز")
        button = st.button("ساختن")
        if button:
            if name and grade:

                x = Curser.execute("INSERT INTO Students (name, lname, grade) VALUES (?, ?, ?)", (name, lname, grade))
                conn.commit()
                st.success("با موفقیت ساخته شد")
    if crud == "خواندن":
        st.title("دسترسی به اطلاعات دانش آموزان")
        Curser.execute("SELECT * FROM students")
        rows = Curser.fetchall()
    
        if rows:
            for row in rows:
                st.subheader(f"شناسه :  {row[0]}")
                st.write(f"نام : {row[1]}")
                st.write(f"نام خانوادگی : {row[2]}")
                st.write(f"معدل : {row[3]}")
        else:
            st.info("هیچ رکوردی موجود نیست.")
    if crud == "بروزرسانی":
        st.title("بروزرسانی اطلاعات")  
        record_id = st.number_input("شناسه رکورد برای به‌روزرسانی", step=1, min_value=1)
        Curser.execute("SELECT * FROM students WHERE id = ?", (record_id,))
        record = Curser.fetchone()

        if record:
            name = st.text_input("نام ", value=record[1])
            lname = st.text_input("نام خانوادگی", value=record[2])
            grade = st.number_input("معدل", value=record[3])
            if st.button("به‌روزرسانی"):
                Curser.execute("UPDATE students SET name = ?, lname = ?, grade = ? WHERE id = ?", (name, lname, grade, record_id))
                conn.commit()
                st.success("رکورد با موفقیت به‌روزرسانی شد!")
        else:
            st.warning("رکوردی با این شناسه یافت نشد.")

    if crud == "حذف":
        st.header("حذف اطلاعات")
        record_id = st.number_input("شناسه اطلاعات برای حذف", step=1, min_value=1)

        Curser.execute("SELECT * FROM students WHERE id = ?", (record_id,))
        record = Curser.fetchone()

        if record:
            if st.button("حذف"):
                Curser.execute("DELETE FROM students WHERE id = ?", (record_id,))
                conn.commit()
                st.success("رکورد با موفقیت حذف شد!")
        else:
            st.warning("رکوردی با این شناسه یافت نشد.")

if operation == "هوش مصنوعی":
        
        st.header(':llama: هوش مصنوعی لاما')
        st.caption("🚀 A Streamlit chatbot powered by  :llama: Llama")
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        prompt = st.chat_input()
        if prompt:
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            with st.spinner('Generating response: '):
                msg = call_llama('llama3.1', prompt)['response']
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)

if __name__ == '__main__':
        model = 'llama3.2'

