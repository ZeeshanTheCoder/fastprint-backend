from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
def send_simple_thank_you_email(user_email):
    """
    Send a simple thank you email after successful payment
    """
    try:
        # Render HTML email template without user name
        html_content = render_to_string('emails/simple_thank_you.html')
        
        # Create plain text version
        text_content = strip_tags(html_content)
        
        subject = "Thank You for Your Purchase!"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user_email]
        
        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Thank you email sent to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send thank you email to {user_email}: {str(e)}")
        return False
