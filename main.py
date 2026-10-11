import streamlit as st
import psycopg2


# Функция коннекта (теперь она берет данные из st.secrets)
def search_letters(user_query):
    try:
        # МАГИЯ: Берем данные базы из секретов Streamlit
        conn = psycopg2.connect(st.secrets["db_url"])
        cur = conn.cursor()

        # Наш крутой SQL с подсветкой
        sql = """
        SELECT folder_num, page_num, sender_full_name, location, 
               ts_headline('russian', content, to_tsquery('russian', %s), 
               'StartSel = <mark>, StopSel = </mark>, HighlightAll=TRUE')
        FROM letters 
        WHERE search_vector @@ to_tsquery('russian', %s)
        """

        formatted_query = " & ".join(user_query.split())
        cur.execute(sql, (formatted_query, formatted_query))
        return cur.fetchall()
    except Exception as e:
        return f"Ошибка подключения к облачной базе: {e}"


# --- ИНТЕРФЕЙС ---
st.set_page_config(page_title="Архив Маяк", page_icon="📜")

st.title("🕯 Поисковая система «Маяк»")
st.subheader("Цифровой архив писем (Облачная версия)")

query = st.text_input("Введите ключевое слово:")

if query:
    results = search_letters(query)

    if isinstance(results, str):
        st.error(results)
    elif results:
        st.info(f"Найдено записей: {len(results)}")
        for row in results:
            with st.expander(f"✉️ {row[2]} ({row[3] if row[3] else 'Город не указан'})"):
                st.write(f"*📍 Архивный адрес:* Папка {row[0]}, Лист {row[1]}")
                st.write("*📄 Текст письма:*")
                # Выводим с подсветкой
                st.markdown(row[4], unsafe_allow_html=True)
    else:
        st.warning("Ничего не нашли")
