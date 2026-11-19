from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ReportedURL

User = get_user_model()


class URLSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=2048)


class ChainReportSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=2048)


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "name", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ReportedURLSSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedURL
        fields = ["id", "url", "reported_date", "confirmed", "chain_tx_hash"]
