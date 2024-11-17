"""
Google Earth Engine authentication script.
Run this first to authenticate with GEE.
"""
import ee

def authenticate_gee():
    """Authenticate with Google Earth Engine."""
    try:
        # Try to initialize with default credentials
        ee.Initialize(project='ee-sergiyk1974')
        print("Successfully initialized with existing credentials")
    except Exception as e:
        print("Authentication required. Opening browser for authentication...")
        # First authenticate
        ee.Authenticate()
        # Then initialize with project ID
        try:
            ee.Initialize(project='ee-sergiyk1974')
            print("Successfully authenticated and initialized Earth Engine")
        except Exception as e:
            print(f"Failed to initialize Earth Engine: {str(e)}")
            raise

if __name__ == "__main__":
    authenticate_gee()
