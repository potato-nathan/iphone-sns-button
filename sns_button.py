"""
SNS Button - Pythonista iOS Application
A simple button app that sends notifications via Amazon SNS.

This application is designed to run on Pythonista for iOS.
"""

import ui
import os
import csv
import json

# Pythonista includes the 'requests' library
import requests


def load_env_file(env_path):
    """
    Load configuration from a .env file.
    
    Args:
        env_path: Path to the .env file
        
    Returns:
        Dictionary of environment variables
    """
    config = {}
    
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Configuration file not found: {env_path}")
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse key=value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config


def load_distribution_list(csv_path):
    """
    Load the distribution list from a CSV file.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        List of dictionaries with recipient information
    """
    recipients = []
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Distribution list not found: {csv_path}")
    
    with open(csv_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            recipients.append({
                'first_name': row.get('First_Name', ''),
                'last_name': row.get('Last_Name', ''),
                'email': row.get('email', ''),
                'phone_number': row.get('phone_number', '')
            })
    
    return recipients


def send_sns_notification(endpoint_url, api_token, message, recipients):
    """
    Send a notification to the Amazon SNS endpoint.
    
    Args:
        endpoint_url: The SNS endpoint URL
        api_token: API token for authentication
        message: The custom message to send
        recipients: List of recipient dictionaries
        
    Returns:
        Tuple of (success: bool, response_message: str)
    """
    try:
        # Prepare the payload
        payload = {
            'message': message,
            'recipients': recipients,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        # Prepare headers with authentication
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_token}',
            'X-Api-Key': api_token
        }
        
        # Send the POST request
        response = requests.post(
            endpoint_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        # Check if the request was successful
        if response.status_code in (200, 201, 202):
            return True, f"Success! Status: {response.status_code}"
        else:
            return False, f"Error: {response.status_code} - {response.text[:100]}"
            
    except requests.exceptions.Timeout:
        return False, "Error: Request timed out"
    except requests.exceptions.ConnectionError:
        return False, "Error: Could not connect to server"
    except Exception as e:
        return False, f"Error: {str(e)}"


class SNSButtonApp:
    """Main application class for the SNS Button app."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = None
        self.recipients = []
        self.view = None
        self.status_label = None
        self.send_button = None
        self.activity_indicator = None
        
        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load configuration
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from .env file and distribution list."""
        try:
            env_path = os.path.join(self.script_dir, '.env')
            self.config = load_env_file(env_path)
            
            # Validate required configuration
            required_keys = ['SNS_ENDPOINT_URL', 'SNS_API_TOKEN', 'BUTTON_NAME', 
                           'DISTRO_LIST_CSV', 'CUSTOM_MESSAGE']
            missing_keys = [key for key in required_keys if key not in self.config]
            
            if missing_keys:
                raise ValueError(f"Missing configuration: {', '.join(missing_keys)}")
            
            # Load distribution list
            csv_path = self.config['DISTRO_LIST_CSV']
            if not os.path.isabs(csv_path):
                csv_path = os.path.join(self.script_dir, csv_path)
            
            self.recipients = load_distribution_list(csv_path)
            
        except Exception as e:
            print(f"Configuration error: {e}")
            raise
    
    def create_ui(self):
        """Create the user interface."""
        # Create main view
        self.view = ui.View()
        self.view.name = 'SNS Notification'
        self.view.background_color = '#1a1a2e'
        
        # Get screen dimensions for responsive layout
        screen_width, screen_height = ui.get_screen_size()
        
        # Create title label
        title_label = ui.Label()
        title_label.text = 'SNS Notification'
        title_label.font = ('<system-bold>', 24)
        title_label.text_color = 'white'
        title_label.alignment = ui.ALIGN_CENTER
        title_label.frame = (20, 60, screen_width - 40, 40)
        title_label.flex = 'W'
        self.view.add_subview(title_label)
        
        # Create info label showing recipient count
        info_label = ui.Label()
        info_label.text = f'Recipients: {len(self.recipients)}'
        info_label.font = ('<system>', 16)
        info_label.text_color = '#888888'
        info_label.alignment = ui.ALIGN_CENTER
        info_label.frame = (20, 110, screen_width - 40, 25)
        info_label.flex = 'W'
        self.view.add_subview(info_label)
        
        # Create the main send button
        self.send_button = ui.Button()
        self.send_button.title = self.config['BUTTON_NAME']
        self.send_button.font = ('<system-bold>', 22)
        self.send_button.tint_color = 'white'
        self.send_button.background_color = '#0f4c75'
        self.send_button.corner_radius = 15
        
        # Center the button
        button_width = min(280, screen_width - 80)
        button_height = 70
        button_x = (screen_width - button_width) / 2
        button_y = (screen_height - button_height) / 2 - 20
        self.send_button.frame = (button_x, button_y, button_width, button_height)
        self.send_button.flex = 'LRTB'
        self.send_button.action = self.button_tapped
        self.view.add_subview(self.send_button)
        
        # Create activity indicator
        self.activity_indicator = ui.ActivityIndicator()
        self.activity_indicator.style = ui.ACTIVITY_INDICATOR_STYLE_WHITE_LARGE
        self.activity_indicator.center = (screen_width / 2, button_y + button_height + 50)
        self.activity_indicator.flex = 'LRTB'
        self.activity_indicator.hides_when_stopped = True
        self.view.add_subview(self.activity_indicator)
        
        # Create status label
        self.status_label = ui.Label()
        self.status_label.text = 'Ready to send notification'
        self.status_label.font = ('<system>', 14)
        self.status_label.text_color = '#cccccc'
        self.status_label.alignment = ui.ALIGN_CENTER
        self.status_label.number_of_lines = 3
        self.status_label.frame = (20, button_y + button_height + 80, screen_width - 40, 80)
        self.status_label.flex = 'WT'
        self.view.add_subview(self.status_label)
        
        # Create message preview label
        message_preview = ui.Label()
        preview_text = self.config['CUSTOM_MESSAGE']
        if len(preview_text) > 50:
            preview_text = preview_text[:50] + '...'
        message_preview.text = f'Message: "{preview_text}"'
        message_preview.font = ('<system>', 12)
        message_preview.text_color = '#666666'
        message_preview.alignment = ui.ALIGN_CENTER
        message_preview.number_of_lines = 2
        message_preview.frame = (20, button_y + button_height + 160, screen_width - 40, 50)
        message_preview.flex = 'WT'
        self.view.add_subview(message_preview)
        
        return self.view
    
    @ui.in_background
    def button_tapped(self, sender):
        """Handle button tap event."""
        # Update UI to show loading state
        self._set_loading_state(True)
        self.status_label.text = 'Sending notification...'
        
        try:
            # Send the notification
            success, message = send_sns_notification(
                self.config['SNS_ENDPOINT_URL'],
                self.config['SNS_API_TOKEN'],
                self.config['CUSTOM_MESSAGE'],
                self.recipients
            )
            
            # Update status based on result
            if success:
                self.status_label.text_color = '#4CAF50'  # Green
                self.status_label.text = f'✓ {message}'
            else:
                self.status_label.text_color = '#f44336'  # Red
                self.status_label.text = f'✗ {message}'
                
        except Exception as e:
            self.status_label.text_color = '#f44336'
            self.status_label.text = f'✗ Error: {str(e)}'
        
        finally:
            # Reset loading state
            self._set_loading_state(False)
    
    def _set_loading_state(self, loading):
        """Set the UI loading state."""
        if loading:
            self.send_button.enabled = False
            self.send_button.alpha = 0.5
            self.activity_indicator.start()
        else:
            self.send_button.enabled = True
            self.send_button.alpha = 1.0
            self.activity_indicator.stop()
    
    def run(self):
        """Run the application."""
        view = self.create_ui()
        view.present('fullscreen')


def main():
    """Main entry point for the application."""
    try:
        app = SNSButtonApp()
        app.run()
    except Exception as e:
        # If there's a configuration error, show a simple error view
        view = ui.View()
        view.name = 'Error'
        view.background_color = '#1a1a2e'
        
        error_label = ui.Label()
        error_label.text = f'Configuration Error:\n\n{str(e)}'
        error_label.font = ('<system>', 16)
        error_label.text_color = '#f44336'
        error_label.alignment = ui.ALIGN_CENTER
        error_label.number_of_lines = 10
        
        screen_width, screen_height = ui.get_screen_size()
        error_label.frame = (20, 100, screen_width - 40, screen_height - 200)
        error_label.flex = 'WH'
        
        view.add_subview(error_label)
        view.present('fullscreen')


if __name__ == '__main__':
    main()
