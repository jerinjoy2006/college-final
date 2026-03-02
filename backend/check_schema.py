import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def check_table(table_name):
    try:
        res = supabase.table(table_name).select("*").limit(1).execute()
        if res.data:
            print(f"Columns in '{table_name}' table:", res.data[0].keys())
        else:
            print(f"'{table_name}' table is empty.")
    except Exception as e:
        print(f"Error fetching from '{table_name}':", e)

check_table("users")
check_table("clubs")
check_table("events")
check_table("registrations")

print("\n--- Testing book_event_seat function exists (expecting error or success) ---")
try:
    # Just a fake call to see if it even resolves
    res = supabase.rpc("book_event_seat", {"p_event_id": "00000000-0000-0000-0000-000000000000", "p_user_id": "00000000-0000-0000-0000-000000000000"}).execute()
    print("book_event_seat exists (result):", res)
except Exception as e:
    # If the function doesn't exist, it usually gives a 404/403 or specific PostgREST error
    print("book_event_seat test failed (expected if non-existent or bad params):", e)
