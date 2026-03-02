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


class SNSButtonView(ui.View):
    """Custom view that handles its own layout."""
    
    def __init__(self, config, recipients):
        super().__init__()
        self.config = config
        self.recipients = recipients
        self.name = 'SNS Notification'
        self.background_color = '#1a1a2e'
        
        # Create title label
        self.title_label = ui.Label()
        self.title_label.text = 'SNS Notification'
        self.title_label.font = ('<system-bold>', 24)
        self.title_label.text_color = 'white'
        self.title_label.alignment = ui.ALIGN_CENTER
        self.add_subview(self.title_label)
        
        # Create info label showing recipient count
        self.info_label = ui.Label()
        self.info_label.text = f'Recipients: {len(self.recipients)}'
        self.info_label.font = ('<system>', 16)
        self.info_label.text_color = '#888888'
        self.info_label.alignment = ui.ALIGN_CENTER
        self.add_subview(self.info_label)
        
        # Create the main send button
        self.send_button = ui.Button()
        self.send_button.title = self.config['BUTTON_NAME']
        self.send_button.font = ('<system-bold>', 22)
        self.send_button.tint_color = 'white'
        self.send_button.background_color = "#b60000"
        self.send_button.corner_radius = 15
        self.send_button.action = self.button_tapped
        self.add_subview(self.send_button)
        
        # Create activity indicator
        self.activity_indicator = ui.ActivityIndicator()
        self.activity_indicator.style = ui.ACTIVITY_INDICATOR_STYLE_WHITE_LARGE
        self.activity_indicator.hides_when_stopped = True
        self.add_subview(self.activity_indicator)
        
        # Create status label
        self.status_label = ui.Label()
        self.status_label.text = 'Ready to send notification'
        self.status_label.font = ('<system>', 14)
        self.status_label.text_color = '#cccccc'
        self.status_label.alignment = ui.ALIGN_CENTER
        self.status_label.number_of_lines = 3
        self.add_subview(self.status_label)
        
        # Create message preview label
        self.message_preview = ui.Label()
        preview_text = self.config['CUSTOM_MESSAGE']
        if len(preview_text) > 50:
            preview_text = preview_text[:50] + '...'
        self.message_preview.text = f'Message: "{preview_text}"'
        self.message_preview.font = ('<system>', 12)
        self.message_preview.text_color = '#666666'
        self.message_preview.alignment = ui.ALIGN_CENTER
        self.message_preview.number_of_lines = 2
        self.add_subview(self.message_preview)
    
    def layout(self):
        """Called automatically when the view is resized."""
        w = self.width
        h = self.height
        
        # Title at top
        self.title_label.frame = (20, 80, w - 40, 40)
        
        # Info label below title
        self.info_label.frame = (20, 130, w - 40, 25)
        
        # Button centered
        button_width = min(280, w - 80)
        button_height = 70
        button_x = (w - button_width) / 2
        button_y = (h - button_height) / 2
        self.send_button.frame = (button_x, button_y, button_width, button_height)
        
        # Activity indicator below button
        self.activity_indicator.center = (w / 2, button_y + button_height + 50)
        
        # Status label below activity indicator
        self.status_label.frame = (20, button_y + button_height + 80, w - 40, 80)
        
        # Message preview at bottom
        self.message_preview.frame = (20, button_y + button_height + 160, w - 40, 50)
    
    @ui.in_background
    def button_tapped(self, sender):
        """Handle button tap event."""
        self._set_loading_state(True)
        self.status_label.text = 'Sending notification...'
        self.status_label.text_color = '#cccccc'
        
        try:
            success, message = send_sns_notification(
                self.config['SNS_ENDPOINT_URL'],
                self.config['SNS_API_TOKEN'],
                self.config['CUSTOM_MESSAGE'],
                self.recipients
            )
            
            if success:
                self.status_label.text_color = '#4CAF50'
                self.status_label.text = f'Success: {message}'
            else:
                self.status_label.text_color = '#f44336'
                self.status_label.text = message
                
        except Exception as e:
            self.status_label.text_color = '#f44336'
            self.status_label.text = f'Error: {str(e)}'
        
        finally:
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


def main():
    """Main entry point for the application."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Load configuration
        env_path = os.path.join(script_dir, 'env.txt')
        config = load_env_file(env_path)
        
        # Validate required configuration
        required_keys = ['SNS_ENDPOINT_URL', 'SNS_API_TOKEN', 'BUTTON_NAME', 
                       'DISTRO_LIST_CSV', 'CUSTOM_MESSAGE']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            raise ValueError(f"Missing configuration: {', '.join(missing_keys)}")
        
        # Load distribution list
        csv_path = config['DISTRO_LIST_CSV']
        if not os.path.isabs(csv_path):
            csv_path = os.path.join(script_dir, csv_path)
        
        recipients = load_distribution_list(csv_path)
        
        # Create and present the view
        view = SNSButtonView(config, recipients)
        view.present('fullscreen')
        
    except Exception as e:
        # Show error view
        view = ui.View()
        view.name = 'Error'
        view.background_color = '#1a1a2e'
        
        error_label = ui.Label()
        error_label.text = f'Configuration Error:\n\n{str(e)}'
        error_label.font = ('<system>', 16)
        error_label.text_color = '#f44336'
        error_label.alignment = ui.ALIGN_CENTER
        error_label.number_of_lines = 10
        error_label.frame = (20, 100, 300, 400)
        error_label.flex = 'WHLRTB'
        
        view.add_subview(error_label)
        view.present('fullscreen')


if __name__ == '__main__':
    main()
