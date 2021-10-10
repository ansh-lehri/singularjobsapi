from rest_framework import serializers
from user_account.models import UserAccount,UserProfileModel


class UserSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(style = {'input_type':'password'}, write_only=True)

    class Meta:

        model = UserAccount
        fields = ['email','username','password','confirm_password']
        extra_kwargs = {
            'password':{'write_only':True},
        }


    def save(self):

        account = UserAccount(email = self.validated_data['email'], username = self.validated_data['username'])
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']

        if password!=confirm_password:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        account.set_password(password)
        account.save()

        return account
        
        

class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfileModel
        fields = ['email','technical_skills','soft_skills','job_types','subject_interest','linkedin_profile']

    
    def create(self,validated_data):
        print(validated_data)
        return UserProfileModel.objects.update_or_create(**validated_data)
























    