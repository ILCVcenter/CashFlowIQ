"""
data/data_loader.py - ניהול טעינת וטיפול בנתונים
"""
import pandas as pd
import streamlit as st

@st.cache_data(ttl=60)  # מטמון לשעה אחת בלבד לאפשר רענון נתונים
def load_data():
    """טעינת נתוני CSV"""
    df = pd.read_csv("data/sample_data.csv")
    return df

def process_uploaded_csv(uploaded_file, existing_data):
    """עיבוד קובץ CSV שהועלה והוספתו לנתונים קיימים"""
    try:
        new_data = pd.read_csv(uploaded_file)
        
        # המרת עמודת התאריך לפורמט אחיד
        if 'date' in new_data.columns:
            # ניסיון להמיר תאריכים בכל פורמט אפשרי
            try:
                new_data['date'] = pd.to_datetime(new_data['date'])
                # המרה לפורמט YYYY-MM-DD אחיד
                new_data['date'] = new_data['date'].dt.strftime('%Y-%m-%d')
                st.success("התאריכים הומרו בהצלחה לפורמט YYYY-MM-DD")
            except Exception as e:
                st.warning(f"שגיאה בהמרת התאריכים: {e}. מנסה פורמט אחר...")
                try:
                    # ניסיון להמיר עם פורמט ספציפי
                    new_data['date'] = pd.to_datetime(new_data['date'], format='%d/%m/%Y')
                    new_data['date'] = new_data['date'].dt.strftime('%Y-%m-%d')
                    st.success("התאריכים הומרו בהצלחה לפורמט YYYY-MM-DD")
                except:
                    st.error("לא ניתן להמיר את התאריכים. אנא בדוק שהתאריכים בפורמט תקין.")
                    return existing_data
        
        # מיזוג הנתונים
        merged_data = pd.concat([existing_data, new_data], ignore_index=True)
        
        # הסרת כפילויות (לפי כל העמודות)
        merged_data = merged_data.drop_duplicates()
        
        # הצגת הודעת הצלחה
        st.success(f"הנתונים נוספו בהצלחה! נוספו {len(new_data)} שורות.")
        
        # אפשרות להציג חלק מהנתונים החדשים
        with st.expander("הצג את הנתונים החדשים שנוספו"):
            st.dataframe(new_data.head(10))
            
        return merged_data
        
    except Exception as e:
        st.error(f"שגיאה בקריאת הקובץ: {e}")
        return existing_data

def save_data_to_source(data):
    """שמירת נתונים לקובץ המקור"""
    try:
        data.to_csv("data/sample_data.csv", index=False)
        st.cache_data.clear()  # מחיקת המטמון כדי לחייב טעינה מחדש
        st.success("הנתונים נשמרו בהצלחה לקובץ המקור! לחץ על Rerun כדי לראות את השינויים.")
        return True
    except Exception as e:
        st.error(f"שגיאה בשמירת הנתונים: {e}")
        return False

def filter_data_by_date_range(data, date_range):
    """סינון נתונים לפי טווח תאריכים"""
    if len(date_range) == 2:
        start_date, end_date = date_range
        data['date'] = pd.to_datetime(data['date'])
        mask = (data['date'] >= pd.Timestamp(start_date)) & (data['date'] <= pd.Timestamp(end_date))
        return data[mask]
    return data

def filter_data_by_categories(data, categories):
    """סינון נתונים לפי קטגוריות"""
    if categories:
        return data[data['category'].isin(categories)]
    return data

def filter_data_by_types(data, types):
    """סינון נתונים לפי סוגים"""
    if types:
        return data[data['type'].isin(types)]
    return data 