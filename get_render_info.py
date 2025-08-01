#!/usr/bin/env python3
"""
Get Render.com account information
"""

import requests
import json

def get_render_account_info():
    """Get Render account information including owner ID"""
    
    render_api_key = "rnd_1q6pIHjPfAZOd8MmgrpN36mVqPbn"
    
    headers = {
        "Authorization": f"Bearer {render_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get account info
        print("Getting Render account information...")
        response = requests.get(
            "https://api.render.com/v1/owners",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            owners = response.json()
            print("Account information:")
            print(json.dumps(owners, indent=2))
            
            if owners and len(owners) > 0:
                owner_id = owners[0].get('id')
                print(f"\nOwner ID: {owner_id}")
                return owner_id
        else:
            print(f"Failed to get account info: {response.status_code}")
            print("Response:", response.text)
        
        # Try getting existing services
        print("\nGetting existing services...")
        response = requests.get(
            "https://api.render.com/v1/services",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            services = response.json()
            print("Existing services:")
            for service in services:
                print(f"- {service.get('name')}: {service.get('id')}")
                if service.get('name') == 'jen-ai-assistant':
                    print(f"  Found existing Jen AI service: {service.get('id')}")
                    return service.get('id')
        else:
            print(f"Failed to get services: {response.status_code}")
            print("Response:", response.text)
        
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    result = get_render_account_info()
    if result:
        print(f"\nResult: {result}")
    else:
        print("\nNo result found")