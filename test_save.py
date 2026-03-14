import sys
import traceback
from backend.database import save_email_analysis, get_db_connection

try:
    save_email_analysis('fake_email', {'priority':'High','summary':'Test','item_name':'Test','quantity':1}, None, None)
    print('Success')
except Exception as e:
    traceback.print_exc()
