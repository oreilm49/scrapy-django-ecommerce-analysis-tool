from rest_framework import serializers

from cms.settings import ADMINS
from cms.tasks import send_email


class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    message = serializers.CharField()

    def send_notification(self):
        html = f'<p>{self.validated_data["name"]}</p>'
        html += f'<p>{self.validated_data["email"]}</p>'
        html += f'<p>{self.validated_data["message"]}</p>'
        send_email.delay('Contact', html, [email for name, email in ADMINS])
