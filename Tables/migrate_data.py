import pandas as pd
import sqlite3

# נתיב לקובץ ה-Excel
excel_path = 'C:/Users/haimk/Downloads/disability_assistance/Tables/Rights Map.xlsx'

# התחברות (או יצירת) מסד הנתונים SQLite
conn = sqlite3.connect('disability_rights.db')
cursor = conn.cursor()

# יצירת טבלאות במסד הנתונים
cursor.execute('''
CREATE TABLE IF NOT EXISTS זכויות (
    id INTEGER PRIMARY KEY,
    שם_הזכות TEXT,
    תיאור_כללי TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS קריטריונים_לזכאות (
    id INTEGER PRIMARY KEY,
    id_זכות INTEGER,
    אחוזי_נכות_מינימליים INTEGER,
    אחוזי_נכות_מקסימליים INTEGER,
    טווח_זמן_מההכרה_כנכה TEXT,
    סוג_פגיעה TEXT,
    האם_נדרש_להיות_הורה_לילדים TEXT,
    עדיפות INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS פרטי_הזכות (
    id INTEGER PRIMARY KEY,
    id_זכות INTEGER,
    טיפול_פרטני TEXT,
    טיפול_משפחתי TEXT,
    תקופת_הסיוע TEXT,
    זיקה_לטיפול_לנכות TEXT,
    תקופה_נוספת TEXT,
    זכאות_לטיפול_לבן_בת_זוג_או_הורה TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS מידע_נוסף (
    id INTEGER PRIMARY KEY,
    id_זכות INTEGER,
    פרטי_מידע_נוספים TEXT,
    קישור_למסמכים TEXT,
    הנחיות_למימוש_הזכאות TEXT
)
''')

# קריאת הגיליונות מה-Excel
xls = pd.ExcelFile(excel_path)

# הכנסת הנתונים לכל טבלה
rights_df = pd.read_excel(xls, 'זכויות')
criteria_df = pd.read_excel(xls, 'קריטריונים לזכאות')
details_df = pd.read_excel(xls, 'פרטי הזכות')
additional_info_df = pd.read_excel(xls, 'מידע נוסף')

# הכנסת הנתונים לטבלת "זכויות"
rights_df.to_sql('זכויות', conn, if_exists='replace', index=False)

# הכנסת הנתונים לטבלת "קריטריונים לזכאות"
criteria_df.to_sql('קריטריונים_לזכאות', conn, if_exists='replace', index=False)

# הכנסת הנתונים לטבלת "פרטי הזכות"
details_df.to_sql('פרטי_הזכות', conn, if_exists='replace', index=False)

# הכנסת הנתונים לטבלת "מידע נוסף"
additional_info_df.to_sql('מידע_נוסף', conn, if_exists='replace', index=False)

# סגירת החיבור למסד הנתונים
conn.close()

print("הנתונים הועברו בהצלחה למסד הנתונים!")
