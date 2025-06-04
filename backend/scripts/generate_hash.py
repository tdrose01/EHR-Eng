import bcrypt

def generate_hash(password):
    """Generate a bcrypt hash for a password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

if __name__ == "__main__":
    password = "admin123"
    hashed = generate_hash(password)
    print(f"Password: {password}")
    print(f"Bcrypt hash: {hashed}")
    
    # Verify the hash
    is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    print(f"Hash verification: {is_valid}") 