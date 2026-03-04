from flask import Flask, render_template, request
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_rights', methods=['POST'])
def check_rights():
    print("\n=== התחלת בדיקת זכויות ===")
    print("כל הנתונים מהטופס:")
    print(request.form)
    
    try:
        # קבלת גיל
        age = int(request.form['age'])
        
        # חישוב אחוזי נכות
        total_disability = 0
        mental_disability = 0
        
        # בדיקה אם יש נכות נפשית
        if request.form.get('mental_disability') == 'yes':
            mental_disability = int(request.form.get('mental_disability_percentage', 0))
            total_disability += mental_disability
        
        # בדיקה אם יש נכויות אחרות
        if request.form.get('other_disability') == 'yes':
            general_disability = int(request.form.get('general_disability_percentage', 0))
            total_disability += general_disability

        # קבלת שאר הנתונים
        head_injury = request.form.get('head_injury') == 'yes'
        lower_limbs_injury = request.form.get('lower_limbs_injury') == 'yes'
        is_parent = request.form.get('is_parent') == 'yes'

        print(f"""
        נתונים שעובדו:
        גיל: {age}
        אחוזי נכות כוללים: {total_disability}
        אחוזי נכות נפשית: {mental_disability}
        פגיעת ראש: {head_injury}
        פגיעה בגפיים: {lower_limbs_injury}
        הורה: {is_parent}
        """)

        # קריאת קובץ הזכויות
        with open('rights-data.json', 'r', encoding='utf-8') as file:
            rights_data = json.load(file)
            print("\nנתונים מקובץ rights-data.json:")
            print(f"מספר הזכויות בקובץ: {len(rights_data['eligibilityCriteria'])}")
            print("\nפירוט כל הזכויות שנטענו:")
            for right in rights_data['eligibilityCriteria']:
                print(f"זכות מספר: {right['rightId']}, domain: {right['domain']}, category: {right['category']}")

        # קביעת סוג הנכות בהתאם לנתונים
        disability_types = []
        if mental_disability > 0:
            disability_types.append("אחוזי נכות נפשיים")
        if head_injury:
            disability_types.append("אחוזי נכות בגין פגיעת ראש")
        if lower_limbs_injury:
            disability_types.append("אחוזי נכות בגין פגיעה בגפיים התחתונות")
        if not disability_types:
            disability_types.append("אחוזי נכות כוללים")

        print("סוגי נכות שזוהו:", disability_types)

        # חיפוש זכויות מתאימות
        matching_rights = []
        for right in rights_data['eligibilityCriteria']:
            print(f"\nבודק זכות: {right['rightId']}")
            
            # בדיקת התאמה לסוג הנכות
            if right['disabilityType'] in disability_types:
                print(f"סוג נכות תואם: {right['disabilityType']}")
                
                # בדיקת אחוזי נכות
                if right['minPercentage'] <= total_disability <= right['maxPercentage']:
                    print(f"אחוזי נכות תואמים: {right['minPercentage']} <= {total_disability} <= {right['maxPercentage']}")
                    
                    # בדיקת דרישת הורות
                    if not right['requiresChildren'] or is_parent:
                        print("דרישת הורות תואמת")
                        matching_rights.append(right)
                    else:
                        print("לא עומד בדרישת הורות")
                else:
                    print(f"אחוזי נכות לא תואמים: {total_disability}")
            else:
                print(f"סוג נכות לא תואם: {right['disabilityType']}")

        print(f"\nנמצאו {len(matching_rights)} זכויות מתאימות")

        # קריאת פרטי הזכויות המלאים
        with open('rights_details.json', 'r', encoding='utf-8') as file:
            rights_details = json.load(file)

        # הכנת המידע המפורט על הזכויות שנמצאו
        detailed_rights = []
        for right in matching_rights:
            right_id = str(right['rightId'])
            if right_id in rights_details['פרטי_זכאויות']:
                detailed_rights.append({
                    'basic_info': right,
                    'details': rights_details['פרטי_זכאויות'][right_id]
                })

        # מיון הזכויות לפי עדיפות
        detailed_rights.sort(key=lambda x: x['basic_info']['subDomainPriority'])

        return render_template('results.html', 
                             rights=detailed_rights,
                             user_data={
                                 'age': age,
                                 'total_disability': total_disability,
                                 'mental_disability': mental_disability,
                                 'is_parent': is_parent,
                                 'head_injury': head_injury,
                                 'lower_limbs_injury': lower_limbs_injury
                             })

    except Exception as e:
        print("שגיאה:", str(e))  # הוספת הדפסת השגיאה לדיבוג
        return f"אירעה שגיאה בעיבוד הבקשה: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)