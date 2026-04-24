"""
Database operations for MySQL via XAMPP with JSON fallback
"""
import mysql.connector
import hashlib
import re
import json
import os
from datetime import datetime, timedelta
from config.settings import DB_CONFIG, OTP_VALIDITY_SECONDS, MAX_OTP_ATTEMPTS

# Fallback JSON storage when MySQL is not available
FALLBACK_USERS_FILE = "data/users_fallback.json"
FALLBACK_OTP_FILE = "data/otps_fallback.json"

def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs("data", exist_ok=True)

def load_fallback_users():
    """Load users from fallback JSON file"""
    ensure_data_dir()
    if os.path.exists(FALLBACK_USERS_FILE):
        with open(FALLBACK_USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_fallback_users(users):
    """Save users to fallback JSON file"""
    ensure_data_dir()
    with open(FALLBACK_USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_fallback_otps():
    """Load OTPs from fallback JSON file"""
    ensure_data_dir()
    if os.path.exists(FALLBACK_OTP_FILE):
        with open(FALLBACK_OTP_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_fallback_otps(otps):
    """Save OTPs to fallback JSON file"""
    ensure_data_dir()
    with open(FALLBACK_OTP_FILE, 'w') as f:
        json.dump(otps, f, indent=4)


# Database Connection
def get_db_connection():
    """Get MySQL database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None


# Validation Functions
def validate_mobile(phone):
    """Validate mobile number - 10 digits starting with 6-9"""
    phone_clean = re.sub(r'[^\d]', '', phone)
    if len(phone_clean) != 10:
        return False, "Mobile number must be exactly 10 digits"
    if phone_clean[0] not in ['6', '7', '8', '9']:
        return False, "Mobile number must start with 6, 7, 8, or 9"
    return True, phone_clean


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_upi_id(upi_id):
    """Validate UPI ID format - must contain @upi"""
    if '@upi' not in upi_id.lower():
        return False
    pattern = r'^[\w\.\-]+@[\w]+$'
    return re.match(pattern, upi_id) is not None


def validate_card_number(card_number):
    """Validate card number (basic validation)"""
    card_number = card_number.replace(" ", "")
    return len(card_number) == 16 and card_number.isdigit()


def validate_cvv(cvv):
    """Validate CVV"""
    return len(cvv) in [3, 4] and cvv.isdigit()


def validate_expiry_date(exp_date):
    """Validate expiry date (MM/YY format)"""
    try:
        if '/' not in exp_date:
            return False
        month, year = exp_date.split('/')
        month = int(month)
        year = int(year) + 2000
        if month < 1 or month > 12:
            return False
        current_date = datetime.now()
        exp_date_obj = datetime(year, month, 1)
        return exp_date_obj >= current_date
    except:
        return False


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


# User Management Functions
def register_user(name, email, phone, password):
    """Register a new user in MySQL database or fallback storage"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "Email already registered!"
            
            # Insert new user
            query = """
            INSERT INTO users (name, email, phone, password) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (name, email, phone, hash_password(password)))
            connection.commit()
            
            return True, "Registration successful!"
            
        except mysql.connector.Error as e:
            print(f"Registration error: {e}")
            return False, "Registration failed"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        # Fallback to JSON storage
        try:
            users = load_fallback_users()
            
            # Check if email already exists
            if email in users:
                return False, "Email already registered!"
            
            # Create new user
            users[email] = {
                'name': name,
                'email': email,
                'phone': phone,
                'password': hash_password(password),
                'registered_date': datetime.now().isoformat(),
                'tickets': []
            }
            
            save_fallback_users(users)
            print(f"✅ User registered in fallback storage: {email}")
            return True, "Registration successful!"
            
        except Exception as e:
            print(f"Fallback registration error: {e}")
            return False, "Registration failed"


def login_user(email, password):
    """Login user with password"""
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed - Please ensure XAMPP MySQL is running"
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        if not user:
            return False, "Email not found!"
        
        if user['password'] != hash_password(password):
            return False, "Incorrect password!"
        
        return True, user
        
    except mysql.connector.Error as e:
        print(f"Login error: {e}")
        return False, "Login failed"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_user_tickets(email):
    """Get user's tickets from database"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT t.*, u.email 
        FROM tickets t 
        JOIN users u ON t.user_id = u.id 
        WHERE u.email = %s 
        ORDER BY t.booking_time DESC
        """
        cursor.execute(query, (email,))
        tickets = cursor.fetchall()
        
        # Convert to format expected by frontend
        formatted_tickets = []
        for ticket in tickets:
            formatted_ticket = {
                'ticket_id': ticket['id'],
                'route_name': ticket['route_name'],
                'bus_name': ticket['bus_name'],
                'stations': ticket['stations_path'],
                'qty': ticket['quantity'],
                'total_fare': float(ticket['total_fare']),
                'distance': ticket['distance_km'],
                'booking_time': ticket['booking_time'].isoformat(),
                'payment_method': ticket['payment_method'],
                'payment_details': json.loads(ticket['payment_details']) if ticket['payment_details'] else {},
                'transaction_id': ticket['transaction_id']
            }
            formatted_tickets.append(formatted_ticket)
        
        return formatted_tickets
        
    except mysql.connector.Error as e:
        print(f"Get tickets error: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def save_user_ticket(email, ticket):
    """Save a ticket for user in database"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_result = cursor.fetchone()
        if not user_result:
            return False
        
        user_id = user_result[0]
        
        # Extract station IDs from stations path (assuming format "[1] Station → [2] Station")
        stations_parts = ticket['stations'].split(' → ')
        start_station_id = int(stations_parts[0].split(']')[0].replace('[', ''))
        end_station_id = int(stations_parts[-1].split(']')[0].replace('[', ''))
        
        # Insert ticket
        query = """
        INSERT INTO tickets (
            user_id, route_name, bus_name, start_station_id, end_station_id,
            stations_path, quantity, distance_km, fare_per_ticket, total_fare,
            payment_method, payment_details, transaction_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        fare_per_ticket = ticket['total_fare'] / ticket['qty']
        payment_details_json = json.dumps(ticket['payment_details'])
        
        cursor.execute(query, (
            user_id, ticket['route_name'], ticket['bus_name'],
            start_station_id, end_station_id, ticket['stations'],
            ticket['qty'], ticket['distance'], fare_per_ticket,
            ticket['total_fare'], ticket['payment_method'],
            payment_details_json, ticket['transaction_id']
        ))
        
        connection.commit()
        return True
        
    except mysql.connector.Error as e:
        print(f"Save ticket error: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# OTP Management Functions
def save_otp(email, otp):
    """Save OTP to database or fallback storage"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Delete any existing OTPs for this email
            cursor.execute("DELETE FROM otps WHERE email = %s", (email,))
            
            # Insert new OTP
            expires_at = datetime.now() + timedelta(seconds=OTP_VALIDITY_SECONDS)
            query = """
            INSERT INTO otps (email, otp, expires_at) 
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (email, otp, expires_at))
            connection.commit()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"Save OTP error: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        # Fallback to JSON storage
        try:
            otps = load_fallback_otps()
            otps[email] = {
                'otp': otp,
                'timestamp': datetime.now().timestamp(),
                'attempts': 0,
                'expires_at': (datetime.now() + timedelta(seconds=OTP_VALIDITY_SECONDS)).timestamp()
            }
            save_fallback_otps(otps)
            print(f"✅ OTP saved to fallback storage for {email}")
            return True
        except Exception as e:
            print(f"Fallback OTP save error: {e}")
            return False


def verify_otp(email, entered_otp):
    """Verify OTP from database or fallback storage"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get OTP record
            query = """
            SELECT * FROM otps 
            WHERE email = %s AND is_used = FALSE 
            ORDER BY created_at DESC LIMIT 1
            """
            cursor.execute(query, (email,))
            otp_record = cursor.fetchone()
            
            if not otp_record:
                return False, "No OTP found for this email"
            
            # Check if expired
            if datetime.now() > otp_record['expires_at']:
                cursor.execute("DELETE FROM otps WHERE email = %s", (email,))
                connection.commit()
                return False, "OTP expired. Please request a new one"
            
            # Check attempts
            if otp_record['attempts'] >= MAX_OTP_ATTEMPTS:
                cursor.execute("DELETE FROM otps WHERE email = %s", (email,))
                connection.commit()
                return False, "Too many failed attempts. Please request a new OTP"
            
            # Verify OTP
            if otp_record['otp'] == entered_otp:
                # Mark as used
                cursor.execute(
                    "UPDATE otps SET is_used = TRUE WHERE id = %s", 
                    (otp_record['id'],)
                )
                connection.commit()
                return True, "OTP verified successfully"
            else:
                # Increment attempts
                cursor.execute(
                    "UPDATE otps SET attempts = attempts + 1 WHERE id = %s", 
                    (otp_record['id'],)
                )
                connection.commit()
                remaining = MAX_OTP_ATTEMPTS - (otp_record['attempts'] + 1)
                return False, f"Invalid OTP. {remaining} attempts remaining"
            
        except mysql.connector.Error as e:
            print(f"Verify OTP error: {e}")
            return False, "OTP verification failed"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        # Fallback to JSON storage
        try:
            otps = load_fallback_otps()
            
            if email not in otps:
                return False, "No OTP found for this email"
            
            otp_data = otps[email]
            current_time = datetime.now().timestamp()
            
            # Check if expired
            if current_time > otp_data['expires_at']:
                del otps[email]
                save_fallback_otps(otps)
                return False, "OTP expired. Please request a new one"
            
            # Check attempts
            if otp_data['attempts'] >= MAX_OTP_ATTEMPTS:
                del otps[email]
                save_fallback_otps(otps)
                return False, "Too many failed attempts. Please request a new OTP"
            
            # Verify OTP
            if otp_data['otp'] == entered_otp:
                del otps[email]
                save_fallback_otps(otps)
                return True, "OTP verified successfully"
            else:
                otp_data['attempts'] += 1
                save_fallback_otps(otps)
                remaining = MAX_OTP_ATTEMPTS - otp_data['attempts']
                return False, f"Invalid OTP. {remaining} attempts remaining"
                
        except Exception as e:
            print(f"Fallback OTP verify error: {e}")
            return False, "OTP verification failed"


def get_remaining_time(email):
    """Get remaining time for OTP in seconds"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            query = """
            SELECT expires_at FROM otps 
            WHERE email = %s AND is_used = FALSE 
            ORDER BY created_at DESC LIMIT 1
            """
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            
            if result:
                expires_at = result[0]
                remaining = (expires_at - datetime.now()).total_seconds()
                return max(0, int(remaining))
            
            return 0
            
        except mysql.connector.Error as e:
            print(f"Get remaining time error: {e}")
            return 0
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        # Fallback to JSON storage
        try:
            otps = load_fallback_otps()
            if email in otps:
                current_time = datetime.now().timestamp()
                remaining = otps[email]['expires_at'] - current_time
                return max(0, int(remaining))
            return 0
        except Exception as e:
            print(f"Fallback get remaining time error: {e}")
            return 0


# Cleanup function (can be called periodically)
def cleanup_expired_otps():
    """Remove expired OTPs from database"""
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM otps WHERE expires_at < NOW() OR is_used = TRUE")
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Cleanup error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()