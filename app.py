
import streamlit as st
import pandas as pd
from io import BytesIO
from twilio.rest import Client

st.title("Twilio 문자 전송 시뮬레이터")

# Twilio 계정 정보 입력
account_sid = st.text_input("Twilio Account SID", type="password")
auth_token = st.text_input("Twilio Auth Token", type="password")
from_number = st.text_input("Twilio 발신번호 (예: +1xxxx)", value="+1")

uploaded_file = st.file_uploader("수신자 목록 업로드 (이름, 전화번호 포함)", type=["xlsx", "csv"])
if uploaded_file and account_sid and auth_token and from_number:
    try:
        if uploaded_file.name.endswith("xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            df = pd.read_csv(uploaded_file)
        st.write("업로드된 목록", df)

        template = st.text_area("문자 템플릿 입력", "예: {이름}님, 오늘 교육은 오후 2시입니다.")

        if st.button("Twilio로 문자 전송"):
            client = Client(account_sid, auth_token)
            sent_messages = []
            for _, row in df.iterrows():
                name = str(row["이름"])
                phone = str(row["전화번호"])
                phone = phone.replace("-", "").replace(" ", "")
                if phone.startswith("0"):
                    phone = "+82" + phone[1:]
                message = template.replace("{이름}", name)
                try:
                    msg = client.messages.create(
                        to=phone,
                        from_=from_number,
                        body=message
                    )
                    status = "성공"
                except Exception as e:
                    status = f"실패: {e}"
                sent_messages.append({"이름": name, "전화번호": phone, "문자내용": message, "상태": status})

            result_df = pd.DataFrame(sent_messages)
            st.success("문자 전송 완료!")
            st.dataframe(result_df)

            buffer = BytesIO()
            result_df.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)

            st.download_button(
                label="전송 결과 다운로드",
                data=buffer,
                file_name="twilio_문자전송결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"오류 발생: {e}")
else:
    st.warning("Twilio 정보와 수신자 파일을 모두 입력해 주세요.")
