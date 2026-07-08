import uuid
import json
from datetime import datetime, timedelta
import random

# Realistic data pools
SPECIALTIES = ["Cardiology", "Neurology", "Oncology", "Endocrinology", "Internal Medicine"]
HOSPITALS = [
    "General Hospital", "City Medical Center", "St. Jude's", "Mercy Hospital", 
    "Memorial Clinic", "University Hospital", "Veterans Affairs Medical Center",
    "Presbyterian Hospital", "Community Health Center", "Mount Sinai"
]
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

PRODUCTS = ["CardioMax", "NeuroShield", "EndoGlow", "OncoCare", "Immuner", "VascuFlow", "DiabetX", "RespiraClear"]

SENTIMENTS = ["positive", "neutral", "negative"]
INTERACTION_TYPES = ["in-person", "phone", "email", "video", "conference"]

def generate_sql():
    sql = "-- MedConnect AI Seed Data SQL Script\n"
    sql += "-- Run this against your database to populate demo data.\n\n"

    # Base timestamps
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # Generate User
    user_id = str(uuid.uuid4())
    sql += f"""INSERT INTO users (id, created_at, updated_at, email, hashed_password, full_name, role, is_active)
VALUES ('{user_id}', '{now_str}', '{now_str}', 'demo@medconnect.com', 'mock', 'Demo User', 'field_rep', true);\n\n"""

    # Generate 10 Doctors
    doctors = []
    for i in range(10):
        doc_id = str(uuid.uuid4())
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        specialty = random.choice(SPECIALTIES)
        hospital = random.choice(HOSPITALS)
        city = random.choice(CITIES)
        email = f"{name.lower().replace(' ', '.')}@example.com"
        phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        doctors.append((doc_id, name, specialty))

        sql += f"""INSERT INTO doctors (id, created_at, updated_at, name, specialty, hospital, city, email, phone)
VALUES ('{doc_id}', '{now_str}', '{now_str}', 'Dr. {name}', '{specialty}', '{hospital}', '{city}', '{email}', '{phone}');\n"""
    
    sql += "\n"

    # Generate Interactions, Follow-ups, and Recommendations for each doctor
    for doc_id, name, specialty in doctors:
        num_interactions = random.randint(2, 5)
        
        for j in range(num_interactions):
            ix_id = str(uuid.uuid4())
            days_ago = random.randint(1, 90)
            ix_date = (now - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            ix_time = (now - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
            
            ix_type = random.choice(INTERACTION_TYPES)
            sentiment = random.choices(SENTIMENTS, weights=[0.6, 0.3, 0.1])[0]
            
            # Select 1-2 random products
            prods = random.sample(PRODUCTS, random.randint(1, 2))
            # Postgres JSON array syntax vs SQLite
            # To be safe across both, we insert as stringified JSON
            prods_json = json.dumps(prods).replace("'", "''")

            raw_notes = f"Discussed recent clinical trials for {', '.join(prods)}. Dr. {name.split(' ')[1]} seemed {sentiment} about the data."
            ai_summary = f"Interaction focused on {', '.join(prods)}. Key takeaway: {sentiment} sentiment observed regarding efficacy."

            sql += f"""INSERT INTO interactions (id, created_at, updated_at, doctor_id, interaction_date, interaction_type, status, raw_notes, ai_summary, sentiment, products_discussed, follow_up_date)
VALUES ('{ix_id}', '{ix_time}', '{ix_time}', '{doc_id}', '{ix_date}', '{ix_type}', 'completed', '{raw_notes}', '{ai_summary}', '{sentiment}', '{prods_json}', NULL);\n"""

            # 30% chance to have a follow-up for this interaction
            if random.random() < 0.3 or j == num_interactions - 1: # Ensure at least one follow-up for the latest interaction
                fu_id = str(uuid.uuid4())
                days_ahead = random.randint(1, 14)
                fu_date = (now + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
                fu_time = (now + timedelta(days=days_ahead)).strftime('%Y-%m-%d %H:%M:%S')
                desc = f"Send detailed clinical trial reports for {prods[0]}."
                priority = random.choice(["medium", "high"])
                status = "pending" if days_ahead > 0 else "completed"

                sql += f"""INSERT INTO follow_ups (id, created_at, updated_at, doctor_id, interaction_id, due_date, description, priority, status)
VALUES ('{fu_id}', '{fu_time}', '{fu_time}', '{doc_id}', '{ix_id}', '{fu_date}', '{desc}', '{priority}', '{status}');\n"""
        
        # Add 1 AI Recommendation per doctor
        rec_id = str(uuid.uuid4())
        rec_title = f"Focus on {specialty} Applications"
        rec_desc = f"Based on previous positive engagement, Dr. {name.split(' ')[1]} is a strong candidate for early adoption of our upcoming line of {specialty} therapeutics. Recommend scheduling an in-person lunch meeting to present upcoming Q4 trial results."
        meta_json = json.dumps({"confidence": random.randint(75, 95), "topics": [specialty, "early adoption"]}).replace("'", "''")
        
        sql += f"""INSERT INTO ai_recommendations (id, created_at, updated_at, doctor_id, title, description, metadata_data, status)
VALUES ('{rec_id}', '{now_str}', '{now_str}', '{doc_id}', '{rec_title}', '{rec_desc}', '{meta_json}', 'active');\n"""

    return sql

if __name__ == "__main__":
    sql_script = generate_sql()
    with open("seed_data.sql", "w") as f:
        f.write(sql_script)
    print("seed_data.sql generated successfully.")
