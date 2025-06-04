from app.database import execute_query, hash_password

def update_admin_password():
    """Update the admin user's password with bcrypt hash."""
    # Generate bcrypt hash for 'admin123'
    password = "admin123"
    hashed_password = hash_password(password)
    
    print(f"Updating admin password...")
    print(f"New bcrypt hash: {hashed_password}")
    
    # Update the admin user's password
    result = execute_query(
        "UPDATE users SET hashed_password = %s WHERE email = %s RETURNING id",
        (hashed_password, "admin@example.com"),
        fetch=True
    )
    
    if result:
        print(f"Admin password updated successfully for user ID: {result[0]['id']}")
    else:
        print("Failed to update admin password")

if __name__ == "__main__":
    update_admin_password() 