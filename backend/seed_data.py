import os
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Role, User, WhatsAppContact, UserContact

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dita_user:12345678@localhost:5432/dita_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed_roles(session):
    roles_data = [
        {
            "name": "KAPOLRI",
            "level": 1,
            "permissions": {
                "manage_users": True,
                "send_whatsapp": True,
                "manage_contacts": True,
                "export_data": True
            }
        },
        {
            "name": "KAPOLDA",
            "level": 2,
            "permissions": {
                "manage_users": False,
                "send_whatsapp": True,
                "manage_contacts": True,
                "export_data": True
            }
        },
        {
            "name": "KAPOLRES",
            "level": 3,
            "permissions": {
                "manage_users": False,
                "send_whatsapp": False,
                "manage_contacts": False,
                "export_data": False
            }
        }
    ]
    
    for role_data in roles_data:
        existing = session.query(Role).filter_by(name=role_data["name"]).first()
        if not existing:
            role = Role(**role_data)
            session.add(role)
            print(f"Created role: {role_data['name']}")
        else:
            print(f"Role already exists: {role_data['name']}")
    
    session.commit()

def seed_users(session):
    users_data = [
        {
            "nrp": "100001",
            "username": "kapolri_admin",
            "password": "kapolri123",
            "full_name": "Admin KAPOLRI",
            "role_name": "KAPOLRI",
            "is_active": True
        },
        {
            "nrp": "200001",
            "username": "kapolda_jatim",
            "password": "kapolda123",
            "full_name": "KAPOLDA Jawa Timur",
            "role_name": "KAPOLDA",
            "is_active": True
        },
        {
            "nrp": "300001",
            "username": "kapolres_surabaya",
            "password": "kapolres123",
            "full_name": "KAPOLRES Surabaya",
            "role_name": "KAPOLRES",
            "is_active": True
        }
    ]
    
    for user_data in users_data:
        existing = session.query(User).filter_by(username=user_data["username"]).first()
        if not existing:
            role = session.query(Role).filter_by(name=user_data["role_name"]).first()
            if role:
                user = User(
                    nrp=user_data["nrp"],
                    username=user_data["username"],
                    password_hash=bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    full_name=user_data["full_name"],
                    role_id=role.id,
                    is_active=user_data["is_active"]
                )
                session.add(user)
                print(f"Created user: {user_data['username']} (password: {user_data['password']})")
            else:
                print(f"Role not found for user: {user_data['username']}")
        else:
            print(f"User already exists: {user_data['username']}")
    
    session.commit()

def seed_whatsapp_contacts(session):
    contacts_data = [
        {
            "name": "WhatsApp Broadcast Group",
            "phone_number": "6281234567890",
            "is_active": True
        },
        {
            "name": "Emergency Contact",
            "phone_number": "6281234567891",
            "is_active": True
        }
    ]
    
    for contact_data in contacts_data:
        existing = session.query(WhatsAppContact).filter_by(phone_number=contact_data["phone_number"]).first()
        if not existing:
            contact = WhatsAppContact(**contact_data)
            session.add(contact)
            print(f"Created contact: {contact_data['name']}")
        else:
            print(f"Contact already exists: {contact_data['name']}")
    
    session.commit()

def assign_contacts_to_users(session):
    kapolri = session.query(User).filter_by(username="kapolri_admin").first()
    kapolda = session.query(User).filter_by(username="kapolda_jatim").first()
    
    contacts = session.query(WhatsAppContact).all()
    
    if kapolri and contacts:
        for contact in contacts:
            existing = session.query(UserContact).filter_by(
                user_id=kapolri.id,
                contact_id=contact.id
            ).first()
            if not existing:
                user_contact = UserContact(
                    user_id=kapolri.id,
                    contact_id=contact.id,
                    can_send=True
                )
                session.add(user_contact)
                print(f"Assigned contact {contact.name} to {kapolri.username}")
    
    if kapolda and contacts:
        for contact in contacts[:1]:
            existing = session.query(UserContact).filter_by(
                user_id=kapolda.id,
                contact_id=contact.id
            ).first()
            if not existing:
                user_contact = UserContact(
                    user_id=kapolda.id,
                    contact_id=contact.id,
                    can_send=True
                )
                session.add(user_contact)
                print(f"Assigned contact {contact.name} to {kapolda.username}")
    
    session.commit()

def main():
    print("Starting database seeding...")
    session = SessionLocal()
    
    try:
        print("\n1. Seeding roles...")
        seed_roles(session)
        
        print("\n2. Seeding users...")
        seed_users(session)
        
        print("\n3. Seeding WhatsApp contacts...")
        seed_whatsapp_contacts(session)
        
        print("\n4. Assigning contacts to users...")
        assign_contacts_to_users(session)
        
        print("\n✓ Database seeding completed successfully!")
        print("\nTest credentials:")
        print("  KAPOLRI    - username: kapolri_admin      password: kapolri123")
        print("  KAPOLDA    - username: kapolda_jatim      password: kapolda123")
        print("  KAPOLRES   - username: kapolres_surabaya  password: kapolres123")
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
