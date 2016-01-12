# Create dummy key for now
SECRET_KEY = '123456789'

# Create in-memory database
DATABASE_FILE = 'squad_db.sqlite' # Rename to <name>.sqlite
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Squad Info
SQUAD_NICK = '32ndRB'
SQUAD_NAME = '32nd Rangers Battalion'
SQUAD_EMAIL = 'church@32ndrangerbattalion.com'
SQUAD_WEB = 'www.32ndrangerbattalion.com'
# Squad Picture must be in a .paa format, and in templates/xml
SQUAD_PICTURE = '32nd_RB_flash.paa'
SQUAD_TITLE = '32nd Ranger Battalion'
