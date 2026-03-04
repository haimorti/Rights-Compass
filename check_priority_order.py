import sqlite3

# התחברות למסד הנתונים
conn = sqlite3.connect('disability_rights.db')
cursor = conn.cursor()

# שליפת שמות העמודות בטבלה "קריטריונים_לזכאות"
print("קריטריונים לזכאות:")
cursor.execute('PRAGMA table_info(קריטריונים_לזכאות)')
criteria_columns = cursor.fetchall()
for column in criteria_columns:
    print(column[1])

# שליפת שמות העמודות בטבלה "פרטי הזכות"
print("\nפרטי הזכות:")
cursor.execute('PRAGMA table_info(פרטי_הזכות)')
details_columns = cursor.fetchall()
for column in details_columns:
    print(column[1])

# סגירת החיבור
conn.close()
