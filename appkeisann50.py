import streamlit as st
import pandas as pd

# CSSで背景色を変更する関数
def set_background_color(color):
    st.markdown(
        f"""     
        <style>
        .stApp {{
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# CSV用のデータ変換関数（エネルギーは整数、その他は小数点第1位まででフォーマット）
@st.cache_data
def convert_df(df):
    df['エネルギー（kcal）'] = df['エネルギー（kcal）'].round(0).astype(int)  # エネルギーは整数
    df['たんぱく質（g）'] = df['たんぱく質（g）'].round(1)  # 小数点第1位
    df['脂質（g）'] = df['脂質（g）'].round(1)  # 小数点第1位
    df['炭水化物（g）'] = df['炭水化物（g）'].round(1)  # 小数点第1位
    df['食塩相当量（g）'] = df['食塩相当量（g）'].round(1)  # 小数点第1位
    return df.to_csv(index=False).encode('utf-8-sig')

# 初期化
if 'food_data' not in st.session_state:
    st.session_state.food_data = pd.DataFrame(columns=['食品名', 'エネルギー（kcal）', 'たんぱく質（g）', '脂質（g）', '炭水化物（g）', '食塩相当量（g）'])
if 'selected_foods' not in st.session_state:
    st.session_state.selected_foods = pd.DataFrame(columns=['食品名', '重量（g）', 'エネルギー（kcal）', 'たんぱく質（g）', '脂質（g）', '炭水化物（g）', '食塩相当量（g）', '材料の説明'])

st.title("栄養価計算アプリ")

# サイドバーのページ選択
page = st.sidebar.selectbox("ページを選択", ["食品データベース登録", "栄養価計算"])

# ページに応じて背景色を変更
if page == "食品データベース登録":
    set_background_color("#d0f0f8")  # 水色
elif page == "栄養価計算":
    set_background_color("#ffd1dc")  # 薄ピンク色

# 食品データベースのアップロード機能
uploaded_file = st.sidebar.file_uploader("食品データベースをアップロード", type=['csv'])
if uploaded_file is not None:
    uploaded_data = pd.read_csv(uploaded_file)
    # アップロードされたデータとセッションのデータをマージ（重複を削除）
    st.session_state.food_data = pd.concat([st.session_state.food_data, uploaded_data]).drop_duplicates().reset_index(drop=True)   

if page == "食品データベース登録":
    # データベース登録用のフォームをサイドバーに表示
    st.sidebar.subheader("新規食品の登録")
    with st.sidebar.form("food_form"):
        food_name = st.text_input("食品名")
        energy = st.number_input("エネルギー（kcal）", min_value=0.0)
        protein = st.number_input("たんぱく質（g）", min_value=0.0)
        fat = st.number_input("脂質（g）", min_value=0.0)
        carbs = st.number_input("炭水化物（g）", min_value=0.0)
        salt = st.number_input("食塩相当量（g）", min_value=0.0)
        submitted = st.form_submit_button("登録")

    # 入力された食品情報を追加
    if submitted and food_name:
        new_food = pd.DataFrame({
            '食品名': [food_name],
            'エネルギー（kcal）': [energy],
            'たんぱく質（g）': [protein],
            '脂質（g）': [fat],
            '炭水化物（g）': [carbs],
            '食塩相当量（g）': [salt]
        })
        # 重複チェックをして新しいデータを追加
        if not st.session_state.food_data['食品名'].isin([food_name]).any():
            st.session_state.food_data = pd.concat([st.session_state.food_data, new_food], ignore_index=True)
        else:
            st.warning(f"{food_name} はすでに登録されています！")

    # メイン画面に食品データを表示
    st.subheader("食品データベース")
    if not st.session_state.food_data.empty:
        st.dataframe(st.session_state.food_data)

        # CSVダウンロード機能の追加
        csv = convert_df(st.session_state.food_data)

        st.download_button(
            label="CSVファイルとしてダウンロード",
            data=csv,
            file_name='food_database.csv',
            mime='text/csv'
        )

        # 移動または削除する食品を選択するセクション
        st.subheader("食品の移動・削除")
        selected_index = st.selectbox("移動または削除する食品を選択", range(len(st.session_state.food_data)), format_func=lambda x: st.session_state.food_data['食品名'].iloc[x])

        # 食品を削除するボタン
        col1, col2, col3 = st.columns(3)  # 3つのカラムを作成

        with col1:
            if st.button("削除"):
                st.session_state.food_data = st.session_state.food_data.drop(selected_index).reset_index(drop=True)
                st.success("食品が削除されました。")

        with col2:
            # 食品を上に移動するボタン
            if st.button("上に移動"):
                if selected_index > 0:
                    st.session_state.food_data.iloc[[selected_index, selected_index - 1]] = st.session_state.food_data.iloc[[selected_index - 1, selected_index]].values
                    st.success("食品が上に移動しました。")
                else:
                    st.warning("最上部の食品は移動できません。")

        with col3:
            # 食品を下に移動するボタン
            if st.button("下に移動"):
                if selected_index < len(st.session_state.food_data) - 1:
                    st.session_state.food_data.iloc[[selected_index, selected_index + 1]] = st.session_state.food_data.iloc[[selected_index + 1, selected_index]].values
                    st.success("食品が下に移動しました。")
                else:
                    st.warning("最下部の食品は移動できません。")

    else:
        st.write("現在、食品データベースにはデータがありません。")    

elif page == "栄養価計算":
    # 栄養価計算のフォームをサイドバーに表示
    st.sidebar.subheader("栄養価計算")
    uploaded_results = st.sidebar.file_uploader("既存データをアップロード", type=['csv'])

   if uploaded_results is not None:
        uploaded_data = pd.read_csv(uploaded_results)
        uploaded_data = uploaded_data[uploaded_data['食品名'] != '合計']
        st.session_state.selected_foods = pd.concat([st.session_state.selected_foods, uploaded_data]).drop_duplicates().reset_index(drop=True)

    if not st.session_state.food_data.empty:
        food_options = st.session_state.food_data['食品名'].tolist()
        selected_food = st.sidebar.selectbox("食品を選択", food_options)
        weight = st.sidebar.number_input("重量（g）", min_value=0.0)
        material_description = st.sidebar.text_input("材料の説明", "")

        if st.sidebar.button("追加"):
            if selected_food and weight > 0:
                food_info = st.session_state.food_data[st.session_state.food_data['食品名'] == selected_food].iloc[0]
                calculated_food = pd.DataFrame({
                    '食品名': [selected_food],
                    '重量（g）': [weight],
                    'エネルギー（kcal）': [food_info['エネルギー（kcal）'] * (weight / 100)],
                    'たんぱく質（g）': [food_info['たんぱく質（g）'] * (weight / 100)],
                    '脂質（g）': [food_info['脂質（g）'] * (weight / 100)],
                    '炭水化物（g）': [food_info['炭水化物（g）'] * (weight / 100)],
                    '食塩相当量（g）': [food_info['食塩相当量（g）'] * (weight / 100)],
                    '材料の説明': [material_description]
                })
                st.session_state.selected_foods = pd.concat([st.session_state.selected_foods, calculated_food], ignore_index=True)

        # 栄養価計算結果を表示
        if not st.session_state.selected_foods.empty:
            st.subheader("選択した食品の栄養価")

            # 栄養価の合計を計算
            total = pd.DataFrame(st.session_state.selected_foods[['エネルギー（kcal）', 'たんぱく質（g）', '脂質（g）', '炭水化物（g）', '食塩相当量（g）']].sum()).T
            total['食品名'] = '合計'
            total['重量（g）'] = ''
            total['材料の説明'] = ''

            display_data = pd.concat([st.session_state.selected_foods, total], ignore_index=True)

            # 表示用データのフォーマット
            display_data['エネルギー（kcal）'] = display_data['エネルギー（kcal）'].round(0).astype(int)
            display_data['たんぱく質（g）'] = display_data['たんぱく質（g）'].round(1)
            display_data['脂質（g）'] = display_data['脂質（g）'].round(1)
            display_data['炭水化物（g）'] = display_data['炭水化物（g）'].round(1)
            display_data['食塩相当量（g）'] = display_data['食塩相当量（g）'].round(1)

            st.dataframe(display_data)

        # PFCバランスの計算
            total_protein = total['たんぱく質（g）'].values[0]
            total_fat = total['脂質（g）'].values[0]
            total_carbs = total['炭水化物（g）'].values[0]
            total_energy = total['エネルギー（kcal）'].values[0]

            # PFCバランスの計算を修正
            if total_energy > 0:  # 総エネルギーがゼロでない場合のみ計算
                protein_percentage = (total_protein * 4 / total_energy) * 100
                fat_percentage = (total_fat * 9 / total_energy) * 100
                carbs_percentage = (total_carbs * 4 / total_energy) * 100

                st.subheader("PFCバランス")
                st.write(f"エネルギー: {total_energy:.2f} kcal")
                st.write(f"たんぱく質:  {protein_percentage:.2f}%")
                st.write(f"脂質: {fat_percentage:.2f}%")
                st.write(f"炭水化物: {carbs_percentage:.2f}%")
            else:
                st.warning("エネルギーがゼロのため、PFCバランスを計算できません。")

            # CSV保存機能
            csv_data = convert_df(display_data)

            st.download_button(
                label="結果をCSVファイルとしてダウンロード",
                data=csv_data,
                file_name='nutrition_results.csv',
                mime='text/csv'
            )

        # リセットボタン
        if st.button("リセット"):
            st.session_state.selected_foods = pd.DataFrame(columns=['食品名', '重量（g）', 'エネルギー（kcal）', 'たんぱく質（g）', '脂質（g）', '炭水化物（g）', '食塩相当量（g）', '材料の説明'])
            st.success("リセットされました。")

        # 食品を削除・移動するセクション
        st.subheader("食品の移動・削除")
        selected_food_index = st.selectbox("移動または削除する食品を選択", range(len(st.session_state.selected_foods)), format_func=lambda x: st.session_state.selected_foods['食品名'].iloc[x])

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("削除", key="delete_selected_food"):
                st.session_state.selected_foods = st.session_state.selected_foods.drop(selected_food_index).reset_index(drop=True)
                st.success("食品が削除されました。")

        with col2:
            if st.button("上に移動", key="move_up_selected_food"):
                if selected_food_index > 0:
                    st.session_state.selected_foods.iloc[[selected_food_index, selected_food_index - 1]] = st.session_state.selected_foods.iloc[[selected_food_index - 1, selected_food_index]].values
                    st.success("食品が上に移動しました。")
                else:
                    st.warning("最上部の食品は移動できません。")

        with col3:
            if st.button("下に移動", key="move_down_selected_food"):
                if selected_food_index < len(st.session_state.selected_foods) - 1:
                    st.session_state.selected_foods.iloc[[selected_food_index, selected_food_index + 1]] = st.session_state.selected_foods.iloc[[selected_food_index + 1, selected_food_index]].values
                    st.success("食品が下に移動しました。")
                else:
                    st.warning("最下部の食品は移動できません。")

    else:
        st.write("現在、選択された食品はありません。")
