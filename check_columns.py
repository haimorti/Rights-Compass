import sqlite3

# התחברות למסד הנתונים
conn = sqlite3.connect('disability_rights.db')
cursor = conn.cursor()

# שליפת שמות העמודות בטבלה "קריטריונים_לזכאות"
cursor.execute('PRAGMA table_info(קריטריונים_לזכאות)')
columns = cursor.fetchall()

# הדפסת שמות העמודות
for column in columns:
    print(column[1])

# סגירת החיבור
conn.close()
