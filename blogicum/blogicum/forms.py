from django.contrib.auth.forms import UserCreationForm


class ProfileCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name',
                  'last_name', 'email')
