from app.database import execute_query, verify_password

def check_admin_hash():
    """Check the admin user's password hash."""
    admin = execute_query(
        "SELECT id, email, hashed_password, full_name, role FROM users WHERE email = %s",
        ("admin@example.com",)
    )
    
    if admin:
        print(f"Admin user found: {admin[0]['email']}")
        print(f"Hashed password: {admin[0]['hashed_password']}")
        
        # Test password verification
        test_password = "admin123"
        is_valid = verify_password(test_password, admin[0]['hashed_password'])
        print(f"Password verification for '{test_password}': {is_valid}")
    else:
        print("Admin user not found")

if __name__ == "__main__":
    check_admin_hash() 