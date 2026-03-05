# Rights Compass – סיכום לוגיקת מערכת

מסמך זה מסכם בשפה פשוטה איך המערכת עובדת בפועל לפי הקוד הקיים.

## 1) מה המערכת עושה
המערכת מציגה טופס שבו המשתמש מזין נתוני פרופיל (גיל, אחוזי נכות, האם יש פגיעת ראש/גפיים, האם הורה לילדים).
לאחר שליחה, השרת בודק התאמה לקריטריונים מתוך `rights-data.json`, מחבר מידע מפורט מתוך `rights_details.json`, ומחזיר דף תוצאות עם הזכויות המתאימות.

## 2) זרימת עבודה (End-to-End)
1. המשתמש פותח את `/` ומקבל את `index.html`.
2. המשתמש מזין נתונים ולוחץ שליחה (`POST` ל-`/check_rights`).
3. השרת (`app.py`) קורא את השדות מהטופס:
   - age
   - mental_disability + mental_disability_percentage
   - other_disability + general_disability_percentage
   - head_injury
   - lower_limbs_injury
   - is_parent
4. השרת מחשב `total_disability` כסכום אחוזי נכות נפשית + אחוזי נכות כללית (אם הוזנו).
5. השרת קובע רשימת `disability_types` רלוונטיים:
   - "אחוזי נכות נפשיים" אם הוזנה נכות נפשית
   - "אחוזי נכות בגין פגיעת ראש" אם סומן פגיעת ראש
   - "אחוזי נכות בגין פגיעה בגפיים התחתונות" אם סומן
   - אם לא זוהה אף סוג ספציפי: "אחוזי נכות כוללים"
6. השרת טוען את `rights-data.json` ומבצע לולאה על כל הקריטריונים.
7. לכל זכות מתבצעות 3 בדיקות:
   - האם `disabilityType` של הזכות נמצא ב-`disability_types`.
   - האם `total_disability` בטווח `minPercentage` עד `maxPercentage`.
   - האם תנאי הורות מתקיים: אם `requiresChildren`=false זה עובר תמיד; אם true צריך `is_parent`=true.
8. זכויות שעוברות את שלוש הבדיקות נכנסות לרשימת `matching_rights`.
9. השרת טוען `rights_details.json`, ולכל זכות תואמת מנסה למצוא פירוט לפי `rightId`.
10. נבנה `detailed_rights` (מידע בסיסי + פירוט), ממוין לפי `subDomainPriority`.
11. מוחזר `results.html` שמציג סיכום נתוני משתמש ורשימת זכויות בקטגוריות מתקפלות.

## 3) מבנה קבצי הנתונים

### rights-data.json
- מכיל מערך `eligibilityCriteria` (55 רשומות).
- כל רשומה מגדירה "כלל זכאות" עם שדות:
  - `rightId` מזהה הזכות
  - `domain` / `category` / `subDomain` חלוקה נושאית
  - `subDomainCode` / `subDomainPriority` קוד ועדיפות
  - `disabilityType` סוג נכות נדרש
  - `minPercentage` / `maxPercentage` טווח אחוזי נכות
  - `requiresChildren` האם הזכות דורשת להיות הורה

### rights_details.json
- מכיל אובייקט `פרטי_זכאויות` עם מפתח לפי `rightId` (כמחרוזת).
- לכל מזהה קיימים:
  - `נתוני_סיווג` (תחום, תת-תחום, מזהה)
  - `מידע_להצגה`:
    - `כותרות`
    - `הערות_חשובות`
    - `תהליך_מימוש_הזכות`
    - `נהלים_למקרים_חריגים` (לא תמיד)
    - `הנחיות_לביצוע...`
    - `מחלקה_אחראית`
    - `קישורים_שימושיים`

## 4) איפה נמצאת לוגיקת הסינון
הלוגיקה המרכזית נמצאת בפונקציה `check_rights()` בקובץ `app.py`:
- קלט מהטופס
- חישוב אחוזים וסוגי נכות
- לולאה על הקריטריונים מה-JSON
- בדיקות התאמה והוספה לרשימת תוצאות
- העשרת התוצאה מפרטי הזכויות

## 5) תפקידי הקבצים העיקריים
- `app.py` – שרת Flask, routes, חישוב זכויות, טעינת JSON, רינדור תוצאות.
- `templates/index.html` – טופס קלט + JavaScript דינמי להצגת/הסתרת שדות.
- `templates/results.html` – הצגת תוצאות מסווגות, אזורים מתקפלים, קישורים.
- `rights-data.json` – טבלת כללי זכאות (המנוע הלוגי).
- `rights_details.json` – תוכן מפורט להצגה על כל זכות.
- `Tables/migrate_data.py` – סקריפט ETL היסטורי מאקסל ל-SQLite (לא חלק מריצה שוטפת של Flask).
- `check_columns.py`, `check_columns_details.py`, `check_priority_order.py` – סקריפטי בדיקה למסד SQLite.
- `update_criteria_table.sql` – SQL לעדכון סכמת הטבלה `קריטריונים_לזכאות`.

## 6) תרשים פשוט
Frontend (`index.html`)
↓
Flask backend (`app.py` / route `/check_rights`)
↓
קריאת `rights-data.json`
↓
סינון לפי `disabilityType` + טווח אחוזים + `requiresChildren`
↓
העשרת תוצאות מתוך `rights_details.json`
↓
מיון לפי `subDomainPriority`
↓
הצגה ב-`results.html`

## 7) נקודות מפתח לזיכרון
- ההחלטה "מי זכאי למה" מבוססת כרגע על 3 תנאים בלבד: סוג נכות, טווח אחוזים, הורות.
- אין שימוש בגיל בחוקי הסינון עצמם (הגיל נאסף ומועבר לתצוגה).
- המערכת לא משתמשת כרגע ב-SQLite בזמן ריצה; היא עובדת ישירות מול שני קבצי JSON.
