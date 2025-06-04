from app.database import execute_query

def check_users():
    users = execute_query("SELECT * FROM users")
    print("Users in database:")
    for user in users:
        print(f"ID: {user['id']}, Email: {user['email']}, Name: {user['full_name']}, Role: {user['role']}")

if __name__ == "__main__":
    check_users() 